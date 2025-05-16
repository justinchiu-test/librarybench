"""
Resource partitioning for the unified concurrent task scheduler.

This module provides functionality for partitioning resources among owners that can be used
by both the render farm manager and scientific computing implementations.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any, Union

from common.core.exceptions import (
    ResourceError,
    ResourceExceededError,
    ResourceNotAvailableError,
)
from common.core.interfaces import ResourceManagerInterface
from common.core.models import (
    BaseJob,
    BaseNode,
    JobStatus,
    NodeStatus,
    Priority,
    ResourceRequirement,
    ResourceType,
    Result,
)
from common.resource_management.allocator import (
    ResourceAllocator,
    ResourceAllocation,
    AllocationStrategy,
)

logger = logging.getLogger(__name__)


class PartitioningPolicy(str, Enum):
    """Policies for resource partitioning."""
    
    FIXED = "fixed"  # Fixed partitioning with guaranteed minimums
    DYNAMIC = "dynamic"  # Dynamic partitioning based on demand
    WEIGHTED = "weighted"  # Weighted partitioning based on priority
    PROPORTIONAL = "proportional"  # Proportional to job counts or requirements
    ADAPTIVE = "adaptive"  # Adaptive based on historical usage


class BorrowingPolicy(str, Enum):
    """Policies for resource borrowing."""
    
    NONE = "none"  # No borrowing allowed
    THRESHOLD = "threshold"  # Borrowing allowed if utilization is below threshold
    PERMISSION = "permission"  # Borrowing requires permission from the lender
    PRIORITY = "priority"  # Higher priority owners can borrow from lower priority
    UNRESTRICTED = "unrestricted"  # Unrestricted borrowing


class ResourcePartitioner(ResourceManagerInterface):
    """
    Partitioner for compute resources.
    
    This class is responsible for:
    1. Partitioning resources among owners (users, clients, etc.)
    2. Enforcing guaranteed minimums and borrowing policies
    3. Dynamically adjusting partitions based on demand
    """
    
    def __init__(
        self,
        allocator: Optional[ResourceAllocator] = None,
        partitioning_policy: PartitioningPolicy = PartitioningPolicy.FIXED,
        borrowing_policy: BorrowingPolicy = BorrowingPolicy.THRESHOLD,
    ):
        """
        Initialize the resource partitioner.
        
        Args:
            allocator: Optional resource allocator to use
            partitioning_policy: Policy for partitioning resources
            borrowing_policy: Policy for resource borrowing
        """
        self.allocator = allocator or ResourceAllocator()
        self.partitioning_policy = partitioning_policy
        self.borrowing_policy = borrowing_policy
        self.borrowing_enabled = borrowing_policy != BorrowingPolicy.NONE
        self.allocation_monitors: Dict[str, Dict[ResourceType, float]] = {}  # owner_id -> resource_type -> utilization
        self.borrowing_thresholds: Dict[ResourceType, float] = {}  # resource_type -> utilization threshold
        self.owner_priorities: Dict[str, int] = {}  # owner_id -> priority level
        self.partition_history: List[Dict[str, Any]] = []  # History of partition adjustments
        self.adaptive_weights: Dict[str, float] = {}  # owner_id -> weight for adaptive partitioning
        
        # Set up allocator
        self.allocator.borrowing_enabled = self.borrowing_enabled
    
    def register_owner(
        self,
        owner_id: str,
        guaranteed_resources: Dict[ResourceType, float],
        max_resources: Optional[Dict[ResourceType, float]] = None,
        priority: int = 1,
    ) -> None:
        """
        Register a resource owner (user, client, etc.).
        
        Args:
            owner_id: ID of the owner
            guaranteed_resources: Dictionary mapping resource types to guaranteed amounts
            max_resources: Dictionary mapping resource types to maximum amounts
            priority: Priority level of the owner (higher values = higher priority)
        """
        # Register with the allocator
        self.allocator.register_owner(owner_id, guaranteed_resources, max_resources)
        
        # Store priority
        self.owner_priorities[owner_id] = priority
        
        # Initialize utilization monitor
        self.allocation_monitors[owner_id] = {}
        
        # For adaptive partitioning, initialize with equal weights
        self.adaptive_weights[owner_id] = 1.0
    
    def set_total_resources(self, resources: Dict[ResourceType, float]) -> None:
        """
        Set the total available resources.
        
        Args:
            resources: Dictionary mapping resource types to total amounts
        """
        self.allocator.update_total_resources(resources)
    
    def set_borrowing_threshold(
        self,
        resource_type: ResourceType,
        threshold: float,
    ) -> None:
        """
        Set the utilization threshold for resource borrowing.
        
        Args:
            resource_type: Type of resource
            threshold: Utilization threshold (0.0 to 1.0)
        """
        self.borrowing_thresholds[resource_type] = max(0.0, min(1.0, threshold))
    
    def allocate_resources(
        self, 
        owners: List[str],
        nodes: List[BaseNode],
    ) -> Dict[str, Dict[ResourceType, float]]:
        """
        Allocate resources to owners based on requirements and current demands.
        
        Args:
            owners: List of job/simulation owners
            nodes: List of available nodes
            
        Returns:
            Dictionary mapping owner IDs to their resource allocations
        """
        allocations: Dict[str, Dict[ResourceType, float]] = {}
        
        # Get the total resources available across all nodes
        total_resources: Dict[ResourceType, float] = {}
        for node in nodes:
            if hasattr(node, 'capabilities'):
                capabilities = node.capabilities
                
                # CPU cores
                if hasattr(capabilities, 'cpu_cores'):
                    resource_type = ResourceType.CPU
                    if resource_type not in total_resources:
                        total_resources[resource_type] = 0.0
                    total_resources[resource_type] += capabilities.cpu_cores
                
                # Memory
                if hasattr(capabilities, 'memory_gb'):
                    resource_type = ResourceType.MEMORY
                    if resource_type not in total_resources:
                        total_resources[resource_type] = 0.0
                    total_resources[resource_type] += capabilities.memory_gb
                
                # GPU
                if hasattr(capabilities, 'gpu_count'):
                    resource_type = ResourceType.GPU
                    if resource_type not in total_resources:
                        total_resources[resource_type] = 0.0
                    total_resources[resource_type] += capabilities.gpu_count
                
                # Storage
                if hasattr(capabilities, 'storage_gb'):
                    resource_type = ResourceType.STORAGE
                    if resource_type not in total_resources:
                        total_resources[resource_type] = 0.0
                    total_resources[resource_type] += capabilities.storage_gb
            elif hasattr(node, 'get_available_resources'):
                # Use the node's method to get available resources
                available = node.get_available_resources()
                
                for resource_type, amount in available.items():
                    if resource_type not in total_resources:
                        total_resources[resource_type] = 0.0
                    total_resources[resource_type] += amount
        
        # Update the total resources in the allocator
        self.allocator.update_total_resources(total_resources)
        
        # Apply partitioning policy
        if self.partitioning_policy == PartitioningPolicy.FIXED:
            # Fixed partitioning based on guaranteed minimums
            for owner_id in owners:
                if owner_id in self.allocator.guaranteed_resources:
                    allocations[owner_id] = self.allocator.guaranteed_resources[owner_id].copy()
        
        elif self.partitioning_policy == PartitioningPolicy.WEIGHTED:
            # Weighted partitioning based on priority
            for resource_type, total_amount in total_resources.items():
                # Calculate total weighted priority
                total_weighted_priority = sum(
                    self.owner_priorities.get(owner_id, 1)
                    for owner_id in owners
                )
                
                # Divide resources proportionally to priority
                unallocated_amount = total_amount
                for owner_id in owners:
                    priority = self.owner_priorities.get(owner_id, 1)
                    
                    # Calculate the weighted share
                    if total_weighted_priority > 0:
                        share = (priority / total_weighted_priority) * total_amount
                    else:
                        share = 0.0
                    
                    # Store the allocation
                    if owner_id not in allocations:
                        allocations[owner_id] = {}
                    
                    allocations[owner_id][resource_type] = share
                    unallocated_amount -= share
                
                # Distribute any remaining resources equally
                if unallocated_amount > 0 and owners:
                    share_per_owner = unallocated_amount / len(owners)
                    
                    for owner_id in owners:
                        allocations[owner_id][resource_type] += share_per_owner
        
        elif self.partitioning_policy == PartitioningPolicy.ADAPTIVE:
            # Adaptive partitioning based on historical usage
            for resource_type, total_amount in total_resources.items():
                # Calculate total weighted priority
                total_weight = sum(
                    self.adaptive_weights.get(owner_id, 1.0)
                    for owner_id in owners
                )
                
                # Divide resources proportionally to weights
                for owner_id in owners:
                    weight = self.adaptive_weights.get(owner_id, 1.0)
                    
                    # Calculate the weighted share
                    if total_weight > 0:
                        share = (weight / total_weight) * total_amount
                    else:
                        share = 0.0
                    
                    # Store the allocation
                    if owner_id not in allocations:
                        allocations[owner_id] = {}
                    
                    allocations[owner_id][resource_type] = share
        
        elif self.partitioning_policy == PartitioningPolicy.PROPORTIONAL:
            # This requires job information which is not directly available here
            # For now, just divide resources equally
            for resource_type, total_amount in total_resources.items():
                if owners:
                    share_per_owner = total_amount / len(owners)
                    
                    for owner_id in owners:
                        if owner_id not in allocations:
                            allocations[owner_id] = {}
                        
                        allocations[owner_id][resource_type] = share_per_owner
        
        elif self.partitioning_policy == PartitioningPolicy.DYNAMIC:
            # Dynamic partitioning is determined at runtime and managed by the allocator
            # Just return the guaranteed minimums for now
            for owner_id in owners:
                if owner_id in self.allocator.guaranteed_resources:
                    allocations[owner_id] = self.allocator.guaranteed_resources[owner_id].copy()
        
        # Record the partition history
        self.partition_history.append({
            "timestamp": datetime.now().isoformat(),
            "partitioning_policy": self.partitioning_policy.value,
            "allocations": {
                owner_id: {resource_type.value: amount for resource_type, amount in resources.items()}
                for owner_id, resources in allocations.items()
            },
            "total_resources": {
                resource_type.value: amount
                for resource_type, amount in total_resources.items()
            },
        })
        
        return allocations
    
    def can_borrow_resources(
        self, 
        from_owner: str,
        to_owner: str,
        amounts: Dict[ResourceType, float],
    ) -> bool:
        """
        Determine if resources can be borrowed from one owner to another.
        
        Args:
            from_owner: The owner lending resources
            to_owner: The owner borrowing resources
            amounts: The resources to borrow by type
            
        Returns:
            True if resources can be borrowed, False otherwise
        """
        if not self.borrowing_enabled:
            return False
        
        # Check borrowing policy
        if self.borrowing_policy == BorrowingPolicy.NONE:
            return False
        
        elif self.borrowing_policy == BorrowingPolicy.THRESHOLD:
            # Check utilization against thresholds
            for resource_type, amount in amounts.items():
                utilization = self.allocation_monitors.get(from_owner, {}).get(resource_type, 0.0)
                threshold = self.borrowing_thresholds.get(resource_type, 0.7)  # Default 70%
                
                if utilization > threshold:
                    return False
        
        elif self.borrowing_policy == BorrowingPolicy.PRIORITY:
            # Check priorities - higher priority owners can borrow from lower
            borrower_priority = self.owner_priorities.get(to_owner, 0)
            lender_priority = self.owner_priorities.get(from_owner, 0)
            
            if borrower_priority <= lender_priority:
                return False
        
        elif self.borrowing_policy == BorrowingPolicy.PERMISSION:
            # Permission-based borrowing requires external confirmation
            # Default to false for now
            return False
        
        # Delegate to allocator for specific resource availability checks
        return self.allocator.can_borrow_resources(from_owner, to_owner, amounts)
    
    def borrow_resources(
        self,
        from_owner: str,
        to_owner: str,
        resources: Dict[ResourceType, float],
    ) -> Result[Dict[ResourceType, float]]:
        """
        Borrow resources from one owner to another.
        
        Args:
            from_owner: The owner lending resources
            to_owner: The owner borrowing resources
            resources: Dictionary mapping resource types to amounts to borrow
            
        Returns:
            Result with dictionary of borrowed resources or error
        """
        if not self.can_borrow_resources(from_owner, to_owner, resources):
            return Result.err(f"Cannot borrow resources from {from_owner} to {to_owner}")
        
        return self.allocator.borrow_resources(from_owner, to_owner, resources)
    
    def return_borrowed_resources(
        self,
        from_owner: str,
        to_owner: str,
        resources: Optional[Dict[ResourceType, float]] = None,
    ) -> Result[Dict[ResourceType, float]]:
        """
        Return previously borrowed resources.
        
        Args:
            from_owner: The owner that borrowed resources
            to_owner: The owner that lent resources
            resources: Optional dictionary of specific resources to return
            
        Returns:
            Result with dictionary of returned resources or error
        """
        return self.allocator.return_borrowed_resources(from_owner, to_owner, resources)
    
    def calculate_resource_usage(
        self,
        owner_id: str,
        jobs: List[BaseJob],
        nodes: List[BaseNode],
    ) -> Dict[ResourceType, float]:
        """
        Calculate the current resource usage for an owner.
        
        Args:
            owner_id: ID of the owner
            jobs: List of jobs
            nodes: List of nodes
            
        Returns:
            Dictionary mapping resource types to usage percentages
        """
        usage = self.allocator.calculate_resource_usage(owner_id, jobs, nodes)
        
        # Update utilization monitor
        self.allocation_monitors[owner_id] = usage
        
        # For adaptive partitioning, update weights based on utilization
        if self.partitioning_policy == PartitioningPolicy.ADAPTIVE:
            # Calculate the average utilization across all resource types
            utilization_values = list(usage.values())
            if utilization_values:
                avg_utilization = sum(utilization_values) / len(utilization_values)
                
                # Adjust weight based on utilization
                # Higher utilization = higher weight in future allocations
                self.adaptive_weights[owner_id] = 0.7 * self.adaptive_weights.get(owner_id, 1.0) + 0.3 * (avg_utilization / 100.0)
        
        return usage
    
    def get_allocation_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of resource allocations.
        
        Returns:
            List of allocation events
        """
        return self.partition_history.copy()
"""
Resource allocation for the unified concurrent task scheduler.

This module provides functionality for allocating resources to jobs that can be used
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
    LogLevel,
    Priority,
    ResourceRequirement,
    ResourceType,
    Result,
)

logger = logging.getLogger(__name__)


class AllocationStrategy(str, Enum):
    """Strategies for resource allocation."""
    
    FAIR_SHARE = "fair_share"  # Distribute resources fairly among users
    PRIORITY_BASED = "priority_based"  # Allocate based on job priority
    DEADLINE_FIRST = "deadline_first"  # Prioritize jobs with imminent deadlines
    RESOURCE_EFFICIENT = "resource_efficient"  # Optimize for resource efficiency
    ENERGY_EFFICIENT = "energy_efficient"  # Optimize for energy efficiency


class ResourceAllocation:
    """A resource allocation for a job or owner."""
    
    def __init__(
        self,
        owner_id: str,
        resources: Dict[ResourceType, float],
        nodes: Optional[List[str]] = None,
        borrowed: Optional[Dict[str, Dict[ResourceType, float]]] = None,
        lent: Optional[Dict[str, Dict[ResourceType, float]]] = None,
    ):
        """
        Initialize a resource allocation.
        
        Args:
            owner_id: ID of the owner of this allocation
            resources: Dictionary mapping resource types to allocated amounts
            nodes: Optional list of node IDs allocated
            borrowed: Optional dictionary mapping owner IDs to borrowed resources
            lent: Optional dictionary mapping owner IDs to lent resources
        """
        self.owner_id = owner_id
        self.resources = resources
        self.nodes = nodes or []
        self.borrowed = borrowed or {}
        self.lent = lent or {}
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.utilization: Dict[ResourceType, float] = {}
    
    def total_allocated(self, resource_type: ResourceType) -> float:
        """
        Get the total allocated amount of a resource type.
        
        Args:
            resource_type: The resource type to check
            
        Returns:
            Total allocated amount
        """
        base = self.resources.get(resource_type, 0.0)
        
        # Add borrowed resources
        for owner_resources in self.borrowed.values():
            base += owner_resources.get(resource_type, 0.0)
        
        # Subtract lent resources
        for owner_resources in self.lent.values():
            base -= owner_resources.get(resource_type, 0.0)
        
        return max(0.0, base)
    
    def is_overallocated(self, resource_type: ResourceType, limit: float) -> bool:
        """
        Check if a resource type is over-allocated.
        
        Args:
            resource_type: The resource type to check
            limit: The allocation limit
            
        Returns:
            True if over-allocated, False otherwise
        """
        return self.total_allocated(resource_type) > limit
    
    def can_borrow(
        self,
        resource_type: ResourceType,
        amount: float,
        limit: float,
    ) -> bool:
        """
        Check if more of a resource can be borrowed.
        
        Args:
            resource_type: The resource type to check
            amount: The amount to borrow
            limit: The borrowing limit
            
        Returns:
            True if the resource can be borrowed, False otherwise
        """
        new_total = self.total_allocated(resource_type) + amount
        return new_total <= limit
    
    def borrow_from(
        self,
        owner_id: str,
        resource_type: ResourceType,
        amount: float,
    ) -> None:
        """
        Borrow resources from another owner.
        
        Args:
            owner_id: ID of the owner to borrow from
            resource_type: The resource type to borrow
            amount: The amount to borrow
        """
        if owner_id not in self.borrowed:
            self.borrowed[owner_id] = {}
        
        if resource_type not in self.borrowed[owner_id]:
            self.borrowed[owner_id][resource_type] = 0.0
        
        self.borrowed[owner_id][resource_type] += amount
    
    def lend_to(
        self,
        owner_id: str,
        resource_type: ResourceType,
        amount: float,
    ) -> None:
        """
        Lend resources to another owner.
        
        Args:
            owner_id: ID of the owner to lend to
            resource_type: The resource type to lend
            amount: The amount to lend
        """
        if owner_id not in self.lent:
            self.lent[owner_id] = {}
        
        if resource_type not in self.lent[owner_id]:
            self.lent[owner_id][resource_type] = 0.0
        
        self.lent[owner_id][resource_type] += amount
    
    def update_utilization(
        self,
        resource_type: ResourceType,
        amount: float,
    ) -> None:
        """
        Update resource utilization.
        
        Args:
            resource_type: The resource type
            amount: The amount currently in use
        """
        self.utilization[resource_type] = amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "owner_id": self.owner_id,
            "resources": {k.value: v for k, v in self.resources.items()},
            "nodes": self.nodes,
            "borrowed": {
                owner: {k.value: v for k, v in resources.items()}
                for owner, resources in self.borrowed.items()
            },
            "lent": {
                owner: {k.value: v for k, v in resources.items()}
                for owner, resources in self.lent.items()
            },
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "utilization": {k.value: v for k, v in self.utilization.items()},
        }


class ResourceAllocator(ResourceManagerInterface):
    """
    Allocator for compute resources.
    
    This class is responsible for:
    1. Tracking available resources
    2. Allocating resources to jobs
    3. Enforcing resource limits
    4. Managing resource borrowing
    """
    
    def __init__(
        self,
        strategy: AllocationStrategy = AllocationStrategy.FAIR_SHARE,
    ):
        """
        Initialize the resource allocator.
        
        Args:
            strategy: Resource allocation strategy
        """
        self.strategy = strategy
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.guaranteed_resources: Dict[str, Dict[ResourceType, float]] = {}
        self.max_resources: Dict[str, Dict[ResourceType, float]] = {}
        self.total_resources: Dict[ResourceType, float] = {}
        self.reserved_resources: Dict[ResourceType, float] = {}
        self.borrowing_enabled = True
    
    def register_owner(
        self,
        owner_id: str,
        guaranteed: Dict[ResourceType, float],
        maximum: Optional[Dict[ResourceType, float]] = None,
    ) -> None:
        """
        Register a resource owner (user, client, etc.).
        
        Args:
            owner_id: ID of the owner
            guaranteed: Dictionary mapping resource types to guaranteed amounts
            maximum: Dictionary mapping resource types to maximum amounts
        """
        self.guaranteed_resources[owner_id] = guaranteed.copy()
        
        if maximum:
            self.max_resources[owner_id] = maximum.copy()
        else:
            # If no maximum specified, use guaranteed values
            self.max_resources[owner_id] = guaranteed.copy()
        
        # Initialize allocation if it doesn't exist
        if owner_id not in self.allocations:
            self.allocations[owner_id] = ResourceAllocation(
                owner_id=owner_id,
                resources={},
            )
    
    def update_total_resources(self, resources: Dict[ResourceType, float]) -> None:
        """
        Update the total available resources.
        
        Args:
            resources: Dictionary mapping resource types to total amounts
        """
        self.total_resources = resources.copy()
        
        # Recalculate reserved resources
        self.reserved_resources = {}
        
        for owner_id, guaranteed in self.guaranteed_resources.items():
            for resource_type, amount in guaranteed.items():
                if resource_type not in self.reserved_resources:
                    self.reserved_resources[resource_type] = 0.0
                
                self.reserved_resources[resource_type] += amount
    
    def allocate_resources(
        self,
        owner_id: str,
        job: BaseJob,
        nodes: List[BaseNode],
    ) -> Result[ResourceAllocation]:
        """
        Allocate resources for a job.
        
        Args:
            owner_id: ID of the owner
            job: The job to allocate resources for
            nodes: Available nodes
            
        Returns:
            Result with resource allocation or error
        """
        if owner_id not in self.allocations:
            # Initialize allocation if it doesn't exist
            self.allocations[owner_id] = ResourceAllocation(
                owner_id=owner_id,
                resources={},
            )
        
        allocation = self.allocations[owner_id]
        
        # Get job requirements
        requirements: Dict[ResourceType, float] = {}
        
        for req in job.resource_requirements:
            if isinstance(req, ResourceRequirement):
                # If it's a ResourceRequirement object
                requirements[req.resource_type] = req.amount
            elif isinstance(req, dict) and "resource_type" in req and "amount" in req:
                # If it's a dictionary with resource_type and amount
                resource_type = req["resource_type"]
                if isinstance(resource_type, str):
                    # Convert string to ResourceType if needed
                    try:
                        resource_type = ResourceType(resource_type)
                    except ValueError:
                        pass
                
                requirements[resource_type] = req["amount"]
        
        # Check if resources are available
        available_nodes = []
        
        for node in nodes:
            # Skip unavailable nodes
            if not node.is_available():
                continue
            
            # Check if the node can accommodate the job
            if hasattr(node, "can_accommodate"):
                # Use node's can_accommodate method if available
                can_accommodate = node.can_accommodate(job.resource_requirements)
            else:
                # Basic implementation
                can_accommodate = True
                for resource_type, amount in requirements.items():
                    available = node.get_available_resources()[resource_type]
                    if available < amount:
                        can_accommodate = False
                        break
            
            if can_accommodate:
                available_nodes.append(node)
        
        if not available_nodes:
            return Result.err("No suitable nodes available for allocation")
        
        # Check resource limits
        for resource_type, amount in requirements.items():
            max_allowed = self.max_resources.get(owner_id, {}).get(resource_type, 0.0)
            currently_allocated = allocation.total_allocated(resource_type)
            
            if currently_allocated + amount > max_allowed:
                # Check if borrowing is possible
                if self.borrowing_enabled:
                    # Try to borrow from other owners
                    needed = currently_allocated + amount - max_allowed
                    borrowed = self._try_borrow(owner_id, resource_type, needed)
                    
                    if borrowed < needed:
                        return Result.err(
                            f"Resource limit exceeded for {resource_type.value}: "
                            f"requested {amount}, already allocated {currently_allocated}, "
                            f"maximum allowed {max_allowed}, borrowed {borrowed}"
                        )
                else:
                    return Result.err(
                        f"Resource limit exceeded for {resource_type.value}: "
                        f"requested {amount}, already allocated {currently_allocated}, "
                        f"maximum allowed {max_allowed}"
                    )
        
        # Allocate resources
        for resource_type, amount in requirements.items():
            if resource_type not in allocation.resources:
                allocation.resources[resource_type] = 0.0
            
            allocation.resources[resource_type] += amount
        
        # Assign node(s)
        selected_node = self._select_best_node(job, available_nodes)
        if selected_node:
            allocation.nodes.append(selected_node.id)
            job.assigned_node_id = selected_node.id
        
        return Result.ok(allocation)
    
    def release_resources(
        self,
        owner_id: str,
        job: BaseJob,
    ) -> Result[ResourceAllocation]:
        """
        Release resources allocated to a job.
        
        Args:
            owner_id: ID of the owner
            job: The job to release resources for
            
        Returns:
            Result with updated resource allocation or error
        """
        if owner_id not in self.allocations:
            return Result.err(f"No allocation found for owner {owner_id}")
        
        allocation = self.allocations[owner_id]
        
        # Get job requirements
        requirements: Dict[ResourceType, float] = {}
        
        for req in job.resource_requirements:
            if isinstance(req, ResourceRequirement):
                # If it's a ResourceRequirement object
                requirements[req.resource_type] = req.amount
            elif isinstance(req, dict) and "resource_type" in req and "amount" in req:
                # If it's a dictionary with resource_type and amount
                resource_type = req["resource_type"]
                if isinstance(resource_type, str):
                    # Convert string to ResourceType if needed
                    try:
                        resource_type = ResourceType(resource_type)
                    except ValueError:
                        pass
                
                requirements[resource_type] = req["amount"]
        
        # Release resources
        for resource_type, amount in requirements.items():
            if resource_type in allocation.resources:
                allocation.resources[resource_type] = max(
                    0.0, allocation.resources[resource_type] - amount
                )
        
        # Remove node assignment
        if job.assigned_node_id in allocation.nodes:
            allocation.nodes.remove(job.assigned_node_id)
        
        job.assigned_node_id = None
        
        # Return borrowed resources if possible
        self._return_borrowed_resources(owner_id)
        
        return Result.ok(allocation)
    
    def can_borrow_resources(
        self,
        from_owner: str,
        to_owner: str,
        resources: Dict[ResourceType, float],
    ) -> bool:
        """
        Check if resources can be borrowed.
        
        Args:
            from_owner: ID of the owner to borrow from
            to_owner: ID of the owner to borrow for
            resources: Dictionary mapping resource types to amounts
            
        Returns:
            True if resources can be borrowed, False otherwise
        """
        if not self.borrowing_enabled:
            return False
        
        if from_owner not in self.allocations or to_owner not in self.allocations:
            return False
        
        from_allocation = self.allocations[from_owner]
        to_allocation = self.allocations[to_owner]
        
        # Check if the lender has enough resources
        for resource_type, amount in resources.items():
            guaranteed = self.guaranteed_resources.get(from_owner, {}).get(resource_type, 0.0)
            currently_allocated = from_allocation.total_allocated(resource_type)
            utilized = from_allocation.utilization.get(resource_type, 0.0)
            
            # Only allow borrowing if the lender has unused resources above their guaranteed amount
            if utilized + amount > guaranteed or currently_allocated - utilized < amount:
                return False
            
            # Check if the borrower would exceed their maximum
            max_allowed = self.max_resources.get(to_owner, {}).get(resource_type, 0.0)
            borrower_allocated = to_allocation.total_allocated(resource_type)
            
            if borrower_allocated + amount > max_allowed:
                return False
        
        return True
    
    def borrow_resources(
        self,
        from_owner: str,
        to_owner: str,
        resources: Dict[ResourceType, float],
    ) -> Result[Dict[ResourceType, float]]:
        """
        Borrow resources from one owner to another.
        
        Args:
            from_owner: ID of the owner to borrow from
            to_owner: ID of the owner to borrow for
            resources: Dictionary mapping resource types to amounts
            
        Returns:
            Result with borrowed resources or error
        """
        if not self.can_borrow_resources(from_owner, to_owner, resources):
            return Result.err("Cannot borrow requested resources")
        
        from_allocation = self.allocations[from_owner]
        to_allocation = self.allocations[to_owner]
        
        # Perform the borrowing
        for resource_type, amount in resources.items():
            to_allocation.borrow_from(from_owner, resource_type, amount)
            from_allocation.lend_to(to_owner, resource_type, amount)
        
        return Result.ok(resources)
    
    def return_borrowed_resources(
        self,
        from_owner: str,
        to_owner: str,
        resources: Optional[Dict[ResourceType, float]] = None,
    ) -> Result[Dict[ResourceType, float]]:
        """
        Return previously borrowed resources.
        
        Args:
            from_owner: ID of the owner that borrowed
            to_owner: ID of the owner that lent
            resources: Dictionary mapping resource types to amounts
            
        Returns:
            Result with returned resources or error
        """
        if from_owner not in self.allocations or to_owner not in self.allocations:
            return Result.err(f"Owner allocation not found")
        
        from_allocation = self.allocations[from_owner]
        to_allocation = self.allocations[to_owner]
        
        if to_owner not in from_allocation.borrowed:
            return Result.err(f"No resources borrowed from {to_owner}")
        
        if from_owner not in to_allocation.lent:
            return Result.err(f"No resources lent to {from_owner}")
        
        returned: Dict[ResourceType, float] = {}
        
        if resources:
            # Return specific resources
            for resource_type, amount in resources.items():
                borrowed_amount = from_allocation.borrowed.get(to_owner, {}).get(resource_type, 0.0)
                lent_amount = to_allocation.lent.get(from_owner, {}).get(resource_type, 0.0)
                
                # Return the minimum of (requested, borrowed, lent)
                return_amount = min(amount, borrowed_amount, lent_amount)
                
                if return_amount > 0:
                    # Update borrower
                    from_allocation.borrowed[to_owner][resource_type] -= return_amount
                    if from_allocation.borrowed[to_owner][resource_type] <= 0:
                        del from_allocation.borrowed[to_owner][resource_type]
                    
                    # Update lender
                    to_allocation.lent[from_owner][resource_type] -= return_amount
                    if to_allocation.lent[from_owner][resource_type] <= 0:
                        del to_allocation.lent[from_owner][resource_type]
                    
                    returned[resource_type] = return_amount
        else:
            # Return all resources
            for resource_type, amount in list(from_allocation.borrowed.get(to_owner, {}).items()):
                # Update borrower
                del from_allocation.borrowed[to_owner][resource_type]
                
                # Update lender
                del to_allocation.lent[from_owner][resource_type]
                
                returned[resource_type] = amount
        
        # Clean up empty dictionaries
        if to_owner in from_allocation.borrowed and not from_allocation.borrowed[to_owner]:
            del from_allocation.borrowed[to_owner]
        
        if from_owner in to_allocation.lent and not to_allocation.lent[from_owner]:
            del to_allocation.lent[from_owner]
        
        return Result.ok(returned)
    
    def calculate_resource_usage(
        self,
        owner_id: str,
        jobs: List[BaseJob],
        nodes: List[BaseNode],
    ) -> Dict[ResourceType, float]:
        """
        Calculate current resource usage for an owner.
        
        Args:
            owner_id: ID of the owner
            jobs: List of jobs
            nodes: List of nodes
            
        Returns:
            Dictionary mapping resource types to usage percentages
        """
        if owner_id not in self.allocations:
            return {}
        
        allocation = self.allocations[owner_id]
        
        # Calculate current usage
        usage: Dict[ResourceType, float] = {}
        
        # Count resources used by running jobs
        for job in jobs:
            # Skip jobs that don't belong to this owner or aren't running
            if getattr(job, "owner_id", None) != owner_id and getattr(job, "client_id", None) != owner_id:
                continue
                
            if job.status != JobStatus.RUNNING:
                continue
            
            # Count resources
            for req in job.resource_requirements:
                if isinstance(req, ResourceRequirement):
                    # If it's a ResourceRequirement object
                    resource_type = req.resource_type
                    amount = req.amount
                elif isinstance(req, dict) and "resource_type" in req and "amount" in req:
                    # If it's a dictionary with resource_type and amount
                    resource_type = req["resource_type"]
                    if isinstance(resource_type, str):
                        # Convert string to ResourceType if needed
                        try:
                            resource_type = ResourceType(resource_type)
                        except ValueError:
                            continue
                    
                    amount = req["amount"]
                else:
                    continue
                
                if resource_type not in usage:
                    usage[resource_type] = 0.0
                
                usage[resource_type] += amount
        
        # Update allocation with current utilization
        for resource_type, amount in usage.items():
            allocation.update_utilization(resource_type, amount)
        
        # Calculate usage percentages
        percentages: Dict[ResourceType, float] = {}
        
        for resource_type, amount in usage.items():
            allocated = allocation.total_allocated(resource_type)
            
            if allocated > 0:
                percentages[resource_type] = min(100.0, (amount / allocated) * 100.0)
            else:
                percentages[resource_type] = 0.0
        
        return percentages
    
    def _select_best_node(
        self,
        job: BaseJob,
        nodes: List[BaseNode],
    ) -> Optional[BaseNode]:
        """
        Select the best node for a job.
        
        Args:
            job: The job to allocate
            nodes: Available nodes
            
        Returns:
            The selected node, or None if no suitable node is found
        """
        if not nodes:
            return None
        
        # Use custom node scoring if available
        if all(hasattr(node, "calculate_performance_score") for node in nodes):
            # Use node's performance scoring method
            scored_nodes = [(node, node.calculate_performance_score(job)) for node in nodes]
            scored_nodes.sort(key=lambda x: x[1], reverse=True)  # Higher score is better
            
            # Return the highest-scoring node
            return scored_nodes[0][0] if scored_nodes else None
        
        # Simple strategy based on current allocation strategy
        if self.strategy == AllocationStrategy.FAIR_SHARE:
            # Choose the node with the lowest current load
            nodes.sort(key=lambda n: sum(n.current_load.values()) if hasattr(n, "current_load") else 0)
            return nodes[0]
        
        elif self.strategy == AllocationStrategy.RESOURCE_EFFICIENT:
            # Find the node with the smallest resource margin that can fit the job
            nodes.sort(key=lambda n: sum(n.get_available_resources().values()))
            return nodes[0]
        
        elif self.strategy == AllocationStrategy.ENERGY_EFFICIENT:
            # Choose the most energy-efficient node
            if all(hasattr(node, "power_efficiency_rating") for node in nodes):
                nodes.sort(key=lambda n: n.power_efficiency_rating, reverse=True)
                return nodes[0]
        
        # Default: return the first available node
        return nodes[0]
    
    def _try_borrow(
        self,
        owner_id: str,
        resource_type: ResourceType,
        amount: float,
    ) -> float:
        """
        Try to borrow resources from other owners.
        
        Args:
            owner_id: ID of the owner requesting resources
            resource_type: Type of resource to borrow
            amount: Amount of resource to borrow
            
        Returns:
            Amount of resource successfully borrowed
        """
        if not self.borrowing_enabled:
            return 0.0
        
        borrowed_total = 0.0
        
        # Try to borrow from each other owner
        for lender_id, allocation in self.allocations.items():
            if lender_id == owner_id:
                continue
            
            # Skip if the lender doesn't have this resource
            guaranteed = self.guaranteed_resources.get(lender_id, {}).get(resource_type, 0.0)
            currently_allocated = allocation.total_allocated(resource_type)
            utilized = allocation.utilization.get(resource_type, 0.0)
            
            # Only allow borrowing if the lender has unused resources above their guaranteed amount
            available_to_borrow = max(0.0, min(
                currently_allocated - utilized,  # Unused allocation
                currently_allocated - guaranteed,  # Amount above guarantee
            ))
            
            if available_to_borrow <= 0:
                continue
            
            # Determine how much to borrow
            to_borrow = min(amount - borrowed_total, available_to_borrow)
            
            if to_borrow <= 0:
                continue
            
            # Try to borrow
            resources_to_borrow = {resource_type: to_borrow}
            result = self.borrow_resources(lender_id, owner_id, resources_to_borrow)
            
            if result.success:
                borrowed_total += to_borrow
            
            # Stop if we've borrowed enough
            if borrowed_total >= amount:
                break
        
        return borrowed_total
    
    def _return_borrowed_resources(self, owner_id: str) -> None:
        """
        Return all borrowed resources that are no longer needed.
        
        Args:
            owner_id: ID of the owner
        """
        if owner_id not in self.allocations:
            return
        
        allocation = self.allocations[owner_id]
        
        # Check each borrowed resource
        for lender_id in list(allocation.borrowed.keys()):
            for resource_type in list(allocation.borrowed.get(lender_id, {}).keys()):
                borrowed_amount = allocation.borrowed[lender_id].get(resource_type, 0.0)
                utilized_amount = allocation.utilization.get(resource_type, 0.0)
                
                # Return resources if utilization allows
                if resource_type in allocation.resources:
                    base_allocation = allocation.resources.get(resource_type, 0.0)
                    
                    if utilized_amount <= base_allocation:
                        # Can return all borrowed for this resource type
                        self.return_borrowed_resources(owner_id, lender_id, {resource_type: borrowed_amount})
                    elif utilized_amount < base_allocation + borrowed_amount:
                        # Can return partial amount
                        excess = (base_allocation + borrowed_amount) - utilized_amount
                        self.return_borrowed_resources(owner_id, lender_id, {resource_type: excess})
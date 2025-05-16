"""Resource partitioning system for the Render Farm Manager using the common library."""

import logging
import math
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple, Any, cast

from common.core.interfaces import ResourceManagerInterface
from common.core.models import (
    BaseJob,
    BaseNode,
    ResourceRequirement,
    ResourceType,
)

from render_farm_manager.core.models_refactored import (
    RenderClient as Client,
    RenderJob,
    RenderNode,
    ResourceAllocation,
    NodeCapabilities,
)
from render_farm_manager.utils.logging import AuditLogger, PerformanceMonitor


class ResourcePartitioner(ResourceManagerInterface):
    """
    Resource partitioning system that manages resource allocation among clients.
    
    This system ensures that clients receive their guaranteed minimum resources
    while allowing flexible overflow usage when capacity is available.
    """
    
    def __init__(
        self,
        audit_logger: AuditLogger,
        performance_monitor: PerformanceMonitor,
        allow_borrowing: bool = True,
        borrowing_limit_percentage: float = 50.0,
    ):
        """
        Initialize the resource partitioner.
        
        Args:
            audit_logger: Logger for audit trail events
            performance_monitor: Monitor for tracking partitioner performance
            allow_borrowing: Whether to allow resource borrowing between clients
            borrowing_limit_percentage: Maximum percentage of guaranteed resources
                that can be borrowed from a client
        """
        self.audit_logger = audit_logger
        self.performance_monitor = performance_monitor
        self.allow_borrowing = allow_borrowing
        self.borrowing_limit_percentage = borrowing_limit_percentage
        self.logger = logging.getLogger("render_farm.resource_partitioner")
        
        # State management for clients and nodes
        self.clients: Dict[str, Client] = {}
        self.nodes: Dict[str, RenderNode] = {}
        self.client_demand: Dict[str, float] = {}
        self.current_allocations: Dict[str, ResourceAllocation] = {}
    
    def add_client(self, client: Client) -> None:
        """
        Add a client to the resource partitioner.
        
        Args:
            client: The client to add
        """
        self.clients[client.id] = client
        self.client_demand[client.id] = 0.0
        
        self.audit_logger.log_event(
            "client_added_to_partitioner",
            f"Client {client.id} ({client.name}) added to resource partitioner",
            client_id=client.id,
            client_name=client.name,
            sla_tier=client.service_tier,
            guaranteed_resources=client.guaranteed_resources,
            max_resources=client.max_resources,
        )
    
    def add_node(self, node: RenderNode) -> None:
        """
        Add a node to the resource partitioner.
        
        Args:
            node: The node to add
        """
        self.nodes[node.id] = node
        
        self.audit_logger.log_event(
            "node_added_to_partitioner",
            f"Node {node.id} ({node.name}) added to resource partitioner",
            node_id=node.id,
            node_name=node.name,
            node_status=node.status,
        )
    
    def update_client_demand(self, client_id: str, demand_percentage: float) -> None:
        """
        Update the demand percentage for a client.
        
        Args:
            client_id: ID of the client
            demand_percentage: The new demand percentage (0-100)
        """
        if client_id in self.client_demand:
            # When the demand changes, we need to reset the resource allocations
            self.current_allocations = {}
            
            # Update the demand
            self.client_demand[client_id] = max(0.0, min(100.0, demand_percentage))
            
            self.audit_logger.log_event(
                "client_demand_updated",
                f"Client {client_id} demand updated to {self.client_demand[client_id]:.2f}%",
                client_id=client_id,
                demand_percentage=self.client_demand[client_id],
            )
    
    def allocate_resources(self, 
                          user_resources: Dict[str, List[ResourceRequirement]],
                          nodes: List[BaseNode]) -> Dict[str, List[str]]:
        """
        Allocate resources to users based on requirements and available nodes.
        
        Args:
            user_resources: Dictionary mapping user IDs to their resource requirements
            nodes: List of available nodes
            
        Returns:
            Dictionary mapping user IDs to lists of allocated node IDs
        """
        # Convert BaseNode to RenderNode if needed
        render_nodes = [node if isinstance(node, RenderNode) else self._convert_to_render_node(node) 
                       for node in nodes]
        
        # Get clients from our internal state if needed
        clients_list = list(self.clients.values())
        
        # If no clients registered, create temporary ones from user_resources
        if not clients_list:
            for user_id in user_resources:
                # Create a temporary client with default values
                clients_list.append(Client(
                    client_id=user_id,
                    name=f"User {user_id}",
                    service_tier="standard",
                    guaranteed_resources=100 // max(1, len(user_resources)),  # Equal share
                    max_resources=100,  # Can use all resources if available
                ))
        
        # Perform resource partitioning using our existing implementation
        allocations = self._allocate_resources_internal(clients_list, render_nodes)
        
        # Convert our internal allocation format to the interface format
        result: Dict[str, List[str]] = {}
        for client_id, allocation in allocations.items():
            result[client_id] = allocation.allocated_nodes
        
        return result
    
    def can_borrow_resources(self, from_user: str, to_user: str, amount: float) -> bool:
        """
        Determine if resources can be borrowed from one user to another.
        
        Args:
            from_user: The user lending resources
            to_user: The user borrowing resources
            amount: The percentage of resources to borrow
            
        Returns:
            True if resources can be borrowed, False otherwise
        """
        # Cannot borrow if borrowing is disabled
        if not self.allow_borrowing:
            return False
        
        # Get client objects from our internal state
        from_client = self.clients.get(from_user)
        to_client = self.clients.get(to_user)
        
        # If we don't have client objects, create temporary ones
        if not from_client:
            from_client = Client(
                client_id=from_user,
                name=f"User {from_user}",
                service_tier="standard",
                guaranteed_resources=50,  # Default guaranteed resources
                max_resources=100,  # Default max resources
            )
        
        if not to_client:
            to_client = Client(
                client_id=to_user,
                name=f"User {to_user}",
                service_tier="standard",
                guaranteed_resources=50,  # Default guaranteed resources
                max_resources=100,  # Default max resources
            )
        
        # Calculate the maximum amount that can be borrowed from this client
        max_borrowable = from_client.guaranteed_resources * (self.borrowing_limit_percentage / 100)
        
        # Check if the requested amount exceeds the limit
        if amount > max_borrowable:
            return False
        
        # Check if the borrowing client would exceed their maximum allocation
        if to_client.guaranteed_resources + amount > to_client.max_resources:
            return False
        
        return True
    
    def calculate_resource_usage(self, user_id: str, jobs: List[BaseJob], nodes: List[BaseNode]) -> float:
        """
        Calculate the current resource usage for a user.
        
        Args:
            user_id: ID of the user
            jobs: List of jobs
            nodes: List of nodes
            
        Returns:
            Percentage of resources currently used by the user
        """
        # Convert to RenderJob and RenderNode if needed
        render_jobs = [job if isinstance(job, RenderJob) else self._convert_to_render_job(job) 
                      for job in jobs]
        render_nodes = [node if isinstance(node, RenderNode) else self._convert_to_render_node(node) 
                       for node in nodes]
        
        # Count nodes currently used by this user
        user_nodes = 0
        total_nodes = len(render_nodes)
        
        for node in render_nodes:
            if node.current_job_id:
                job = next((j for j in render_jobs if j.id == node.current_job_id), None)
                if job and hasattr(job, 'client_id') and job.client_id == user_id:
                    user_nodes += 1
        
        # Calculate percentage
        if total_nodes == 0:
            return 0.0
        
        return (user_nodes / total_nodes) * 100
    
    def _allocate_resources_internal(
        self, clients: List[Client], nodes: List[RenderNode]
    ) -> Dict[str, ResourceAllocation]:
        """
        Internal implementation of resource allocation.
        
        Args:
            clients: List of clients
            nodes: List of available render nodes
            
        Returns:
            Dictionary mapping client IDs to their resource allocations
        """
        with self.performance_monitor.time_operation("allocate_resources"):
            # Calculate total available resources (number of nodes)
            total_nodes = len(nodes)
            
            # Calculate guaranteed resources for each client
            guaranteed_allocations: Dict[str, int] = {}
            for client in clients:
                # Calculate how many nodes the client is guaranteed
                guaranteed_nodes = math.floor(total_nodes * client.guaranteed_resources / 100)
                guaranteed_allocations[client.id] = guaranteed_nodes
            
            # Check if total guaranteed resources exceed total available resources
            total_guaranteed = sum(guaranteed_allocations.values())
            if total_guaranteed > total_nodes:
                # Scale down guaranteed allocations proportionally
                scale_factor = total_nodes / total_guaranteed
                for client_id in guaranteed_allocations:
                    guaranteed_allocations[client_id] = math.floor(
                        guaranteed_allocations[client_id] * scale_factor
                    )
                
                self.audit_logger.log_event(
                    "resource_allocation_scaled",
                    f"Guaranteed allocations scaled down due to resource constraints (factor: {scale_factor:.2f})",
                    scale_factor=scale_factor,
                    original_total_guaranteed=total_guaranteed,
                    scaled_total_guaranteed=sum(guaranteed_allocations.values()),
                )
            
            # Calculate unallocated nodes
            allocated_nodes = sum(guaranteed_allocations.values())
            unallocated_nodes = total_nodes - allocated_nodes
            
            # Prepare resource allocations
            allocations: Dict[str, ResourceAllocation] = {}
            for client in clients:
                allocations[client.id] = ResourceAllocation(
                    client_id=client.id,
                    allocated_percentage=(guaranteed_allocations[client.id] / total_nodes) * 100 if total_nodes > 0 else 0,
                    allocated_nodes=[],
                    borrowed_percentage=0.0,
                    borrowed_from={},
                    lent_percentage=0.0,
                    lent_to={},
                )
            
            # Allocate guaranteed nodes to clients
            available_nodes = list(nodes)  # Make a copy to track available nodes
            
            for client in clients:
                # Get nodes for this client's guaranteed allocation
                client_nodes = self._select_nodes_for_client(
                    client, 
                    available_nodes, 
                    guaranteed_allocations[client.id]
                )
                
                allocations[client.id].allocated_nodes = [node.id for node in client_nodes]
                
                # Remove allocated nodes from available nodes
                available_nodes = [
                    node for node in available_nodes 
                    if node.id not in allocations[client.id].allocated_nodes
                ]
            
            # If resource borrowing is enabled, handle overflow allocation
            if self.allow_borrowing and unallocated_nodes > 0:
                # Calculate demand for each client (based on pending jobs)
                client_demand = self.client_demand
                if not client_demand:
                    client_demand = self._calculate_client_demand(clients, nodes, allocations)
                
                # Allocate overflow resources based on demand and max allocation limits
                overflow_allocations = self._allocate_overflow_resources(
                    clients, available_nodes, client_demand
                )
                
                # Update allocations with overflow
                for client_id, overflow_nodes in overflow_allocations.items():
                    # Calculate borrowed percentage
                    borrowed_percentage = (len(overflow_nodes) / total_nodes) * 100
                    
                    # Make sure borrowed percentage doesn't exceed the limit for borrowing client
                    client_obj = next((c for c in clients if c.id == client_id), None)
                    if client_obj and self.borrowing_limit_percentage > 0:
                        # Calculate maximum borrowable percentage based on client's guaranteed resources
                        max_borrowable = self.borrowing_limit_percentage
                        if borrowed_percentage > max_borrowable:
                            # Adjust overflow nodes to respect the limit
                            nodes_to_use = math.floor((max_borrowable / 100.0) * total_nodes)
                            # Make sure we always get at least one node if there are any
                            nodes_to_use = max(1, nodes_to_use) if overflow_nodes else 0
                            overflow_nodes = overflow_nodes[:nodes_to_use]
                            borrowed_percentage = (len(overflow_nodes) / total_nodes) * 100
                    
                    # Add overflow nodes to allocation
                    allocations[client_id].allocated_nodes.extend(overflow_nodes)
                    allocations[client_id].allocated_percentage += borrowed_percentage
                    allocations[client_id].borrowed_percentage = borrowed_percentage
                    
                    # Track which clients the resources were borrowed from
                    borrowed_from = {}
                    for other_client in clients:
                        if other_client.id != client_id:
                            borrowed_from[other_client.id] = borrowed_percentage / (len(clients) - 1)
                    
                    allocations[client_id].borrowed_from = borrowed_from
                    
                    # Update lent_to for other clients
                    for other_client_id in borrowed_from:
                        if other_client_id in allocations:
                            if client_id not in allocations[other_client_id].lent_to:
                                allocations[other_client_id].lent_to[client_id] = 0.0
                            
                            allocations[other_client_id].lent_to[client_id] += borrowed_from[other_client_id]
                            allocations[other_client_id].lent_percentage += borrowed_from[other_client_id]
            
            # Log allocations
            for client_id, allocation in allocations.items():
                self.audit_logger.log_event(
                    "resources_allocated",
                    f"Resources allocated to client {client_id}: "
                    f"{allocation.allocated_percentage:.2f}% "
                    f"({len(allocation.allocated_nodes)} nodes)",
                    client_id=client_id,
                    allocated_percentage=allocation.allocated_percentage,
                    allocated_node_count=len(allocation.allocated_nodes),
                    borrowed_percentage=allocation.borrowed_percentage,
                    lent_percentage=allocation.lent_percentage,
                    total_nodes=total_nodes,
                )
            
            # Update our internal state
            self.current_allocations = allocations
            
            # Update performance metrics
            for client_id, allocation in allocations.items():
                self.performance_monitor.update_client_resource_metrics(
                    client_id=client_id,
                    allocated_percentage=allocation.allocated_percentage,
                    borrowed_percentage=allocation.borrowed_percentage,
                    lent_percentage=allocation.lent_percentage,
                )
            
            return allocations
    
    def _select_nodes_for_client(
        self, client: Client, available_nodes: List[RenderNode], node_count: int
    ) -> List[RenderNode]:
        """
        Select appropriate nodes for a client based on their requirements.
        
        Args:
            client: The client to select nodes for
            available_nodes: List of available nodes
            node_count: Number of nodes to select
            
        Returns:
            List of selected nodes
        """
        if node_count <= 0 or not available_nodes:
            return []
        
        # In a real implementation, this would consider the client's typical workload
        # For simplicity, we'll just select the first N available nodes
        return available_nodes[:node_count]
    
    def _calculate_client_demand(
        self, 
        clients: List[Client], 
        nodes: List[RenderNode],
        allocations: Dict[str, ResourceAllocation],
    ) -> Dict[str, float]:
        """
        Calculate resource demand for each client based on pending jobs.
        
        Args:
            clients: List of clients
            nodes: List of nodes
            allocations: Current resource allocations
            
        Returns:
            Dictionary mapping client IDs to their demand (percentage of total resources)
        """
        # This is a simplified implementation - a real system would analyze job requirements
        # and estimate the actual resource needs based on job characteristics
        
        client_demand: Dict[str, float] = {}
        total_nodes = len(nodes)
        
        for client in clients:
            # Check if client is already at their maximum allocation
            if client.max_resources <= 0:
                client_demand[client.id] = 0.0
                continue
            
            current_allocation = allocations[client.id].allocated_percentage
            
            if current_allocation >= client.max_resources:
                client_demand[client.id] = 0.0
            else:
                # Client can use more resources up to their maximum
                client_demand[client.id] = min(
                    client.max_resources - current_allocation,
                    client.guaranteed_resources * 0.5,  # Simplified demand estimation
                )
        
        return client_demand
    
    def _allocate_overflow_resources(
        self,
        clients: List[Client],
        available_nodes: List[RenderNode],
        client_demand: Dict[str, float],
    ) -> Dict[str, List[str]]:
        """
        Allocate overflow resources based on client demand.
        
        Args:
            clients: List of clients
            available_nodes: List of available nodes
            client_demand: Dictionary mapping client IDs to their demand
            
        Returns:
            Dictionary mapping client IDs to lists of allocated overflow node IDs
        """
        overflow_allocations: Dict[str, List[str]] = defaultdict(list)
        
        # Calculate total demand
        total_demand = sum(client_demand.values())
        
        if total_demand <= 0:
            return overflow_allocations
        
        # Sort clients by demand (highest first)
        sorted_clients = sorted(
            [(client_id, demand) for client_id, demand in client_demand.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        
        # Allocate overflow nodes proportionally to demand
        nodes_remaining = len(available_nodes)
        
        for client_id, demand in sorted_clients:
            if demand <= 0 or nodes_remaining <= 0:
                continue
            
            # Calculate share of overflow based on demand
            demand_share = demand / total_demand
            node_share = min(math.floor(demand_share * len(available_nodes)), nodes_remaining)
            
            # Get the nodes for this client
            client_nodes = available_nodes[:node_share]
            overflow_allocations[client_id] = [node.id for node in client_nodes]
            
            # Update remaining nodes
            available_nodes = available_nodes[node_share:]
            nodes_remaining -= node_share
        
        # If there are still nodes available, allocate them to clients that can use them
        while available_nodes and sorted_clients:
            client_id, demand = sorted_clients[0]
            
            if demand > 0:
                overflow_allocations[client_id].append(available_nodes[0].id)
                available_nodes = available_nodes[1:]
            
            # Move this client to the end of the list for round-robin allocation
            sorted_clients = sorted_clients[1:] + [sorted_clients[0]]
        
        return overflow_allocations
    
    def _convert_to_render_job(self, job: BaseJob) -> RenderJob:
        """
        Convert a BaseJob to a RenderJob with default values for render-specific fields.
        
        Args:
            job: The BaseJob to convert
            
        Returns:
            RenderJob based on the BaseJob
        """
        import datetime
        # Create a basic RenderJob with required fields
        render_job = RenderJob(
            id=job.id,
            name=job.name,
            client_id="default_client",  # Default value
            job_type="default",  # Default value
            deadline=datetime.datetime.now() + datetime.timedelta(hours=24),  # Default 24-hour deadline
            estimated_duration_hours=1.0,  # Default 1-hour duration
            memory_requirements_gb=4,  # Default 4GB memory
            cpu_requirements=2,  # Default 2 cores
            output_path="/tmp/output",  # Default output path
            scene_complexity=5,  # Default medium complexity
        )
        
        # Copy base fields
        render_job.status = job.status
        render_job.priority = job.priority
        render_job.submission_time = job.submission_time
        render_job.dependencies = job.dependencies
        render_job.assigned_node_id = job.assigned_node_id
        render_job.error_count = job.error_count
        render_job.progress = job.progress
        
        # Convert resource requirements if available
        if job.resource_requirements:
            for req in job.resource_requirements:
                if req.resource_type == ResourceType.CPU:
                    render_job.cpu_requirements = int(req.amount)
                elif req.resource_type == ResourceType.MEMORY:
                    render_job.memory_requirements_gb = int(req.amount)
                elif req.resource_type == ResourceType.GPU and req.amount > 0:
                    render_job.requires_gpu = True
        
        return render_job
    
    def _convert_to_render_node(self, node: BaseNode) -> RenderNode:
        """
        Convert a BaseNode to a RenderNode with default values for render-specific fields.
        
        Args:
            node: The BaseNode to convert
            
        Returns:
            RenderNode based on the BaseNode
        """
        # Create default capabilities based on node resources
        capabilities = NodeCapabilities(
            cpu_cores=int(node.resources.get(ResourceType.CPU, 4)),
            memory_gb=int(node.resources.get(ResourceType.MEMORY, 16)),
            gpu_model="generic" if ResourceType.GPU in node.resources else None,
            gpu_count=int(node.resources.get(ResourceType.GPU, 0)),
            gpu_memory_gb=float(node.resources.get(ResourceType.GPU, 0)) * 4.0,  # 4GB per GPU
            gpu_compute_capability=1.0 if ResourceType.GPU in node.resources else 0.0,
            storage_gb=int(node.resources.get(ResourceType.STORAGE, 100)),
        )
        
        # Create a RenderNode with the basic properties
        render_node = RenderNode(
            id=node.id,
            name=node.name,
            status=node.status,
            capabilities=capabilities,
            power_efficiency_rating=80.0,  # Default good efficiency
        )
        
        # Copy the rest of the base node properties
        render_node.current_job_id = node.current_job_id
        render_node.uptime_hours = node.uptime_hours
        render_node.last_error = node.last_error
        render_node.resources = node.resources
        
        return render_node
"""Refactored core interfaces for the Render Farm Manager using the common library."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Union

from common.core.interfaces import (
    AuditLogInterface,
    ResourceManagerInterface,
    SchedulerInterface,
    CheckpointManagerInterface,
)
from common.core.models import (
    AuditLogEntry,
    BaseJob,
    BaseNode,
    LogLevel,
)

from render_farm_manager.core.models_refactored import (
    Client,
    EnergyMode,
    ProgressiveOutputConfig,
    RenderJob,
    RenderNode,
    ResourceAllocation,
)


class RenderSchedulerInterface(SchedulerInterface):
    """Interface for the render job scheduling component."""
    
    # All core methods are inherited from common.core.interfaces.SchedulerInterface


class RenderResourceManagerInterface(ResourceManagerInterface):
    """Interface for the render farm resource management component."""
    
    @abstractmethod
    def allocate_client_resources(self, clients: List[Client], nodes: List[RenderNode]) -> Dict[str, ResourceAllocation]:
        """
        Allocate resources to clients based on SLAs and current demands.
        
        Args:
            clients: List of clients
            nodes: List of available render nodes
            
        Returns:
            Dictionary mapping client IDs to their resource allocations
        """
        pass
    
    # Other methods are inherited from common.core.interfaces.ResourceManagerInterface


class NodeSpecializationInterface(ABC):
    """Interface for the node specialization component."""
    
    @abstractmethod
    def match_job_to_node(self, job: RenderJob, nodes: List[RenderNode]) -> Optional[str]:
        """
        Match a job to the most appropriate node based on job requirements and node capabilities.
        
        Args:
            job: The render job to match
            nodes: List of available render nodes
            
        Returns:
            ID of the matched node, or None if no suitable node is found
        """
        pass
    
    @abstractmethod
    def calculate_performance_score(self, job: RenderJob, node: RenderNode) -> float:
        """
        Calculate a performance score for a job on a specific node.
        
        Args:
            job: The render job to evaluate
            node: The render node to evaluate
            
        Returns:
            Performance score (higher is better)
        """
        pass
    
    @abstractmethod
    def update_performance_history(self, job: RenderJob, node: RenderNode, performance_metrics: Dict[str, float]) -> None:
        """
        Update performance history for a node based on completed job metrics.
        
        Args:
            job: The completed render job
            node: The render node that executed the job
            performance_metrics: Metrics about the job's performance
        """
        pass


class ProgressiveResultInterface(ABC):
    """Interface for the progressive result generation component."""
    
    @abstractmethod
    def schedule_progressive_output(
        self, job: RenderJob, config: ProgressiveOutputConfig
    ) -> List[datetime]:
        """
        Schedule progressive output generation for a job.
        
        Args:
            job: The render job
            config: Configuration for progressive output generation
            
        Returns:
            List of scheduled times for progressive output generation
        """
        pass
    
    @abstractmethod
    def generate_progressive_output(self, job: RenderJob, quality_level: int) -> str:
        """
        Generate a progressive output for a job at a specific quality level.
        
        Args:
            job: The render job
            quality_level: Quality level for the progressive output
            
        Returns:
            Path to the generated progressive output
        """
        pass
    
    @abstractmethod
    def estimate_overhead(self, job: RenderJob, config: ProgressiveOutputConfig) -> float:
        """
        Estimate the overhead of progressive output generation for a job.
        
        Args:
            job: The render job
            config: Configuration for progressive output generation
            
        Returns:
            Estimated overhead as a percentage of total rendering time
        """
        pass


class EnergyOptimizationInterface(ABC):
    """Interface for the energy optimization component."""
    
    @abstractmethod
    def optimize_energy_usage(self, jobs: List[RenderJob], nodes: List[RenderNode]) -> Dict[str, str]:
        """
        Optimize energy usage by scheduling jobs to energy-efficient nodes.
        
        Args:
            jobs: List of render jobs
            nodes: List of render nodes
            
        Returns:
            Dictionary mapping job IDs to node IDs based on energy optimization
        """
        pass
    
    @abstractmethod
    def calculate_energy_cost(self, job: RenderJob, node: RenderNode, start_time: datetime) -> float:
        """
        Calculate the energy cost for a job on a specific node.
        
        Args:
            job: The render job
            node: The render node
            start_time: The scheduled start time for the job
            
        Returns:
            Estimated energy cost in currency units
        """
        pass
    
    @abstractmethod
    def get_time_of_day_energy_price(self, time: datetime) -> float:
        """
        Get the energy price for a specific time of day.
        
        Args:
            time: The time to check
            
        Returns:
            Energy price in currency units per kWh
        """
        pass
    
    @abstractmethod
    def set_energy_mode(self, mode: EnergyMode) -> None:
        """
        Set the energy usage mode for the render farm.
        
        Args:
            mode: The energy mode to set
        """
        pass


class RenderAuditInterface(AuditLogInterface):
    """Interface for the render farm audit trail component."""
    
    # All methods are inherited from common.core.interfaces.AuditLogInterface
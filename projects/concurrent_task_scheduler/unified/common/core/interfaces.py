"""
Core interfaces for the unified concurrent task scheduler.

This module defines abstract interfaces that are shared between 
the render farm manager and scientific computing implementations.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Union, Any

from common.core.models import (
    AuditLogEntry,
    BaseJob,
    BaseNode,
    Checkpoint, 
    CheckpointType,
    Dependency,
    DependencyState,
    DependencyType,
    JobStatus,
    NodeStatus,
    Priority,
    ResourceRequirement,
    ResourceType,
    Result,
    TimeRange,
)


class SchedulerInterface(ABC):
    """Interface for the job scheduling component."""
    
    @abstractmethod
    def schedule_jobs(self, jobs: List[BaseJob], nodes: List[BaseNode]) -> Dict[str, str]:
        """
        Schedule jobs to nodes based on priority, deadlines, and resource requirements.
        
        Args:
            jobs: List of jobs to schedule
            nodes: List of available nodes
            
        Returns:
            Dictionary mapping job IDs to node IDs
        """
        pass
    
    @abstractmethod
    def update_priorities(self, jobs: List[BaseJob]) -> List[BaseJob]:
        """
        Update job priorities based on deadlines and completion status.
        
        Args:
            jobs: List of jobs
            
        Returns:
            List of updated jobs with adjusted priorities
        """
        pass
    
    @abstractmethod
    def can_meet_deadline(self, job: BaseJob, available_nodes: List[BaseNode]) -> bool:
        """
        Determine if a job's deadline can be met with available resources.
        
        Args:
            job: The job to evaluate
            available_nodes: List of available nodes
            
        Returns:
            True if the deadline can be met, False otherwise
        """
        pass
    
    @abstractmethod
    def should_preempt(self, running_job: BaseJob, pending_job: BaseJob) -> bool:
        """
        Determine if a running job should be preempted for a pending job.
        
        Args:
            running_job: The currently running job
            pending_job: The job that might preempt the running job
            
        Returns:
            True if the running job should be preempted, False otherwise
        """
        pass


class ResourceManagerInterface(ABC):
    """Interface for the resource management component."""
    
    @abstractmethod
    def allocate_resources(
        self, owners: List[str], nodes: List[BaseNode]
    ) -> Dict[str, Dict[ResourceType, float]]:
        """
        Allocate resources to owners based on requirements and current demands.
        
        Args:
            owners: List of job/simulation owners
            nodes: List of available nodes
            
        Returns:
            Dictionary mapping owner IDs to their resource allocations
        """
        pass
    
    @abstractmethod
    def can_borrow_resources(
        self, from_owner: str, to_owner: str, amounts: Dict[ResourceType, float]
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
        pass
    
    @abstractmethod
    def calculate_resource_usage(
        self, owner_id: str, jobs: List[BaseJob], nodes: List[BaseNode]
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
        pass


class DependencyTrackerInterface(ABC):
    """Interface for the dependency tracking component."""
    
    @abstractmethod
    def add_dependency(
        self, from_id: str, to_id: str, dependency_type: DependencyType = DependencyType.SEQUENTIAL
    ) -> Result[bool]:
        """
        Add a dependency between two jobs or stages.
        
        Args:
            from_id: ID of the prerequisite job/stage
            to_id: ID of the dependent job/stage
            dependency_type: Type of dependency
            
        Returns:
            Result with success status
        """
        pass
    
    @abstractmethod
    def remove_dependency(self, from_id: str, to_id: str) -> Result[bool]:
        """
        Remove a dependency between two jobs or stages.
        
        Args:
            from_id: ID of the prerequisite job/stage
            to_id: ID of the dependent job/stage
            
        Returns:
            Result with success status
        """
        pass
    
    @abstractmethod
    def is_ready_to_run(self, job_id: str, completed_ids: Set[str]) -> bool:
        """
        Check if a job/stage is ready to run based on its dependencies.
        
        Args:
            job_id: ID of the job/stage to check
            completed_ids: Set of IDs that have been completed
            
        Returns:
            True if ready to run, False otherwise
        """
        pass
    
    @abstractmethod
    def get_dependencies_for(self, job_id: str) -> List[Dependency]:
        """
        Get all dependencies for a job/stage.
        
        Args:
            job_id: ID of the job/stage
            
        Returns:
            List of dependencies
        """
        pass
    
    @abstractmethod
    def get_dependents_for(self, job_id: str) -> List[Dependency]:
        """
        Get all jobs/stages that depend on the given job/stage.
        
        Args:
            job_id: ID of the job/stage
            
        Returns:
            List of dependencies
        """
        pass


class CheckpointManagerInterface(ABC):
    """Interface for the checkpoint management component."""
    
    @abstractmethod
    def create_checkpoint(
        self, job_id: str, checkpoint_type: CheckpointType = CheckpointType.FULL
    ) -> Result[Checkpoint]:
        """
        Create a checkpoint for a job/simulation.
        
        Args:
            job_id: ID of the job/simulation
            checkpoint_type: Type of checkpoint to create
            
        Returns:
            Result with the created checkpoint
        """
        pass
    
    @abstractmethod
    def restore_checkpoint(self, checkpoint_id: str) -> Result[bool]:
        """
        Restore a job/simulation from a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            
        Returns:
            Result with success status
        """
        pass
    
    @abstractmethod
    def get_latest_checkpoint(self, job_id: str) -> Optional[Checkpoint]:
        """
        Get the latest checkpoint for a job/simulation.
        
        Args:
            job_id: ID of the job/simulation
            
        Returns:
            The latest checkpoint, or None if no checkpoints exist
        """
        pass
    
    @abstractmethod
    def list_checkpoints(self, job_id: str) -> List[Checkpoint]:
        """
        List all checkpoints for a job/simulation.
        
        Args:
            job_id: ID of the job/simulation
            
        Returns:
            List of checkpoints
        """
        pass


class AuditLogInterface(ABC):
    """Interface for the audit logging component."""
    
    @abstractmethod
    def log_event(
        self, event_type: str, description: str, **details
    ) -> AuditLogEntry:
        """
        Log an event in the audit trail.
        
        Args:
            event_type: Type of event
            description: Human-readable description of the event
            **details: Additional details about the event
            
        Returns:
            The created audit log entry
        """
        pass
    
    @abstractmethod
    def get_events(
        self, 
        job_id: Optional[str] = None,
        node_id: Optional[str] = None,
        owner_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[AuditLogEntry]:
        """
        Get events from the audit log with optional filtering.
        
        Args:
            job_id: Optional filter by job ID
            node_id: Optional filter by node ID
            owner_id: Optional filter by owner ID
            event_type: Optional filter by event type
            start_time: Optional filter by start time
            end_time: Optional filter by end time
            
        Returns:
            List of matching audit log entries
        """
        pass


class ResourceForecastingInterface(ABC):
    """Interface for the resource forecasting component."""
    
    @abstractmethod
    def generate_forecast(
        self,
        owner_id: str,
        resource_type: ResourceType,
        start_date: datetime,
        end_date: datetime,
    ) -> Result[Dict[datetime, float]]:
        """
        Generate a resource usage forecast.
        
        Args:
            owner_id: ID of the owner/project
            resource_type: Type of resource to forecast
            start_date: Start date for the forecast
            end_date: End date for the forecast
            
        Returns:
            Result with dictionary mapping dates to forecasted values
        """
        pass
    
    @abstractmethod
    def train_model(
        self,
        owner_id: str,
        resource_type: ResourceType,
        training_days: int = 30,
    ) -> Result[bool]:
        """
        Train a forecasting model for a specific owner and resource type.
        
        Args:
            owner_id: ID of the owner/project
            resource_type: Type of resource to forecast
            training_days: Number of days of historical data to use
            
        Returns:
            Result with success status
        """
        pass
    
    @abstractmethod
    def evaluate_accuracy(
        self,
        owner_id: str,
        resource_type: ResourceType,
    ) -> Result[Dict[str, float]]:
        """
        Evaluate the accuracy of the forecasting model.
        
        Args:
            owner_id: ID of the owner/project
            resource_type: Type of resource to evaluate
            
        Returns:
            Result with dictionary of accuracy metrics
        """
        pass
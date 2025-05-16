"""Core interfaces for concurrent task scheduling."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from common.core.models import (
    AuditLogEntry,
    BaseJob,
    BaseNode,
    Checkpoint,
    CheckpointType,
    Dependency,
    DependencyType,
    JobStatus,
    LogLevel,
    Priority,
    ResourceRequirement,
    Result,
)


class SchedulerInterface(ABC):
    """Interface for job scheduling components."""
    
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
    """Interface for resource management components."""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass


class ResourceForecastingInterface(ABC):
    """Interface for resource forecasting components."""
    
    @abstractmethod
    def forecast_usage(self, user_id: str, 
                     start_time: datetime, 
                     end_time: datetime) -> Dict[str, List[float]]:
        """
        Forecast resource usage for a specified time period.
        
        Args:
            user_id: ID of the user
            start_time: Start time for the forecast
            end_time: End time for the forecast
            
        Returns:
            Dictionary mapping resource types to lists of forecasted values
        """
        pass
    
    @abstractmethod
    def update_forecast_model(self, 
                            historical_usage: Dict[str, List[Tuple[datetime, float]]]) -> Result[bool]:
        """
        Update the forecasting model with historical usage data.
        
        Args:
            historical_usage: Dictionary mapping resource types to lists of 
                             (timestamp, usage) tuples
            
        Returns:
            Result indicating success or failure of the update
        """
        pass
    
    @abstractmethod
    def predict_resource_requirements(self, job: BaseJob) -> List[ResourceRequirement]:
        """
        Predict resource requirements for a job based on historical data.
        
        Args:
            job: The job to predict requirements for
            
        Returns:
            Predicted resource requirements
        """
        pass


class DependencyTrackerInterface(ABC):
    """Interface for dependency tracking components."""
    
    @abstractmethod
    def register_dependency(self, 
                           from_job_id: str, 
                           to_job_id: str, 
                           dependency_type: DependencyType = DependencyType.SEQUENTIAL,
                           condition: Optional[str] = None) -> Result[bool]:
        """
        Register a dependency between two jobs.
        
        Args:
            from_job_id: ID of the job that must complete first
            to_job_id: ID of the job that depends on the first
            dependency_type: Type of dependency
            condition: Optional condition for conditional dependencies
            
        Returns:
            Result indicating success or failure of the registration
        """
        pass
    
    @abstractmethod
    def check_dependency(self, 
                        from_job_id: str, 
                        to_job_id: str) -> Result[bool]:
        """
        Check if a dependency is satisfied.
        
        Args:
            from_job_id: ID of the job that must complete first
            to_job_id: ID of the job that depends on the first
            
        Returns:
            Result with True if the dependency is satisfied, False otherwise
        """
        pass
    
    @abstractmethod
    def get_dependencies(self, job_id: str, as_source: bool = False) -> Result[List[Dependency]]:
        """
        Get dependencies for a job.
        
        Args:
            job_id: ID of the job
            as_source: If True, return dependencies where this job is the source,
                     otherwise return dependencies where this job is the target
            
        Returns:
            Result with a list of dependencies
        """
        pass
    
    @abstractmethod
    def has_cycle(self) -> Result[Optional[List[str]]]:
        """
        Check if there's a cycle in the dependency graph.
        
        Returns:
            Result with a list of job IDs forming a cycle, or None if no cycle exists
        """
        pass


class CheckpointManagerInterface(ABC):
    """Interface for checkpoint management components."""
    
    @abstractmethod
    def create_checkpoint(self, 
                        job_id: str, 
                        checkpoint_type: CheckpointType = CheckpointType.FULL,
                        metadata: Optional[Dict[str, Any]] = None) -> Result[Checkpoint]:
        """
        Create a checkpoint for a job.
        
        Args:
            job_id: ID of the job
            checkpoint_type: Type of checkpoint
            metadata: Optional metadata for the checkpoint
            
        Returns:
            Result with the created checkpoint
        """
        pass
    
    @abstractmethod
    def list_checkpoints(self, job_id: str) -> Result[List[Checkpoint]]:
        """
        List checkpoints for a job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Result with a list of checkpoints
        """
        pass
    
    @abstractmethod
    def restore_checkpoint(self, checkpoint_id: str) -> Result[bool]:
        """
        Restore a job from a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            
        Returns:
            Result indicating success or failure of the restoration
        """
        pass
    
    @abstractmethod
    def delete_checkpoint(self, checkpoint_id: str) -> Result[bool]:
        """
        Delete a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            
        Returns:
            Result indicating success or failure of the deletion
        """
        pass


class AuditLogInterface(ABC):
    """Interface for audit logging components."""
    
    @abstractmethod
    def log_event(self, 
                event_type: str, 
                description: str, 
                level: LogLevel = LogLevel.INFO,
                job_id: Optional[str] = None,
                node_id: Optional[str] = None,
                user_id: Optional[str] = None,
                **details) -> AuditLogEntry:
        """
        Log an event in the audit trail.
        
        Args:
            event_type: Type of event
            description: Human-readable description of the event
            level: Log level
            job_id: Optional ID of the related job
            node_id: Optional ID of the related node
            user_id: Optional ID of the related user
            **details: Additional details about the event
            
        Returns:
            The created audit log entry
        """
        pass
    
    @abstractmethod
    def get_job_history(self, job_id: str) -> List[AuditLogEntry]:
        """
        Get the audit history for a specific job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            List of audit log entries related to the job
        """
        pass
    
    @abstractmethod
    def get_node_history(self, node_id: str) -> List[AuditLogEntry]:
        """
        Get the audit history for a specific node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            List of audit log entries related to the node
        """
        pass
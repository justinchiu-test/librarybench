"""Core simulation models and definitions, refactored to use the common library."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Union, Any

from pydantic import Field

from common.core.models import (
    BaseJob,
    BaseNode,
    JobStatus,
    NodeStatus as CommonNodeStatus,
    Priority,
    ResourceRequirement,
    ResourceType,
)


class SimulationStageStatus(str, Enum):
    """Status of a simulation stage."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationStage(BaseJob):
    """A single stage in a multi-stage simulation workflow."""

    description: Optional[str] = None
    estimated_duration: timedelta
    dependencies: Set[str] = Field(default_factory=set)
    status: SimulationStageStatus = SimulationStageStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    checkpoint_frequency: timedelta = Field(default=timedelta(hours=1))
    last_checkpoint_time: Optional[datetime] = None
    checkpoint_path: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
    
    # Compatibility methods with BaseJob
    @property
    def progress(self) -> float:
        """Get the simulation stage progress."""
        return super().progress  # Use the progress from BaseJob
    
    @progress.setter
    def progress(self, value: float):
        """Set the simulation stage progress."""
        super().progress = value  # Set the progress on BaseJob


class SimulationStatus(str, Enum):
    """Status of a simulation."""

    DEFINED = "defined"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class Simulation(BaseJob):
    """A complete simulation with multiple stages."""

    description: Optional[str] = None
    stages: Dict[str, SimulationStage]
    status: SimulationStatus = SimulationStatus.DEFINED
    creation_time: datetime = Field(default_factory=datetime.now)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict)
    result_path: Optional[str] = None
    scientific_promise: float = 0.5  # Scale of 0-1 for prioritization
    estimated_total_duration: timedelta = Field(default=timedelta(days=1))
    
    class Config:
        arbitrary_types_allowed = True
    
    @property
    def progress(self) -> float:
        """Get the simulation progress. Alias for total_progress."""
        # For compatibility with tests that expect a progress property
        # Access metadata if it's there, otherwise calculate from stages
        if "progress" in self.metadata:
            return float(self.metadata["progress"])
        return self.total_progress()

    def total_progress(self) -> float:
        """Calculate the total progress of the simulation."""
        if not self.stages:
            return 0.0
        
        total_progress = sum(stage.progress for stage in self.stages.values())
        return total_progress / len(self.stages)
    
    def estimated_completion_time(self) -> Optional[datetime]:
        """Estimate the completion time based on progress and elapsed time."""
        if self.status not in [SimulationStatus.RUNNING, SimulationStatus.PAUSED]:
            return None
        
        if self.start_time is None:
            return None
        
        progress = self.total_progress()
        if progress <= 0:
            return None
        
        elapsed_time = datetime.now() - self.start_time
        total_estimated_time = elapsed_time / progress
        remaining_time = total_estimated_time - elapsed_time
        
        return datetime.now() + remaining_time
    
    def get_active_stage_ids(self) -> List[str]:
        """Get the IDs of all currently active stages."""
        return [
            stage_id for stage_id, stage in self.stages.items()
            if stage.status == SimulationStageStatus.RUNNING
        ]
    
    def get_pending_stage_ids(self) -> List[str]:
        """Get the IDs of all pending stages."""
        return [
            stage_id for stage_id, stage in self.stages.items()
            if stage.status == SimulationStageStatus.PENDING
        ]
    
    def get_next_stages(self) -> List[str]:
        """Get the IDs of stages that are ready to run based on dependencies."""
        result = []
        for stage_id, stage in self.stages.items():
            if stage.status != SimulationStageStatus.PENDING:
                continue
            
            dependencies_met = True
            for dep_id in stage.dependencies:
                if dep_id not in self.stages:
                    dependencies_met = False
                    break
                
                dep_stage = self.stages[dep_id]
                if dep_stage.status != SimulationStageStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                result.append(stage_id)
        
        return result
    
    def update_status(self) -> None:
        """Update the overall simulation status based on stage statuses."""
        if all(stage.status == SimulationStageStatus.COMPLETED for stage in self.stages.values()):
            self.status = SimulationStatus.COMPLETED
            if self.end_time is None:
                self.end_time = datetime.now()
        elif any(stage.status == SimulationStageStatus.FAILED for stage in self.stages.values()):
            self.status = SimulationStatus.FAILED
        elif any(stage.status == SimulationStageStatus.RUNNING for stage in self.stages.values()):
            self.status = SimulationStatus.RUNNING
            if self.start_time is None:
                self.start_time = datetime.now()
        elif any(stage.status == SimulationStageStatus.PAUSED for stage in self.stages.values()):
            self.status = SimulationStatus.PAUSED
        elif all(stage.status in [SimulationStageStatus.PENDING, SimulationStageStatus.QUEUED]
                 for stage in self.stages.values()):
            self.status = SimulationStatus.SCHEDULED


class NodeStatus(str, Enum):
    """Status of a compute node."""
    
    # Include common statuses
    ONLINE = CommonNodeStatus.ONLINE
    OFFLINE = CommonNodeStatus.OFFLINE
    MAINTENANCE = CommonNodeStatus.MAINTENANCE
    ERROR = CommonNodeStatus.ERROR
    STARTING = CommonNodeStatus.STARTING
    STOPPING = CommonNodeStatus.STOPPING
    
    # Add domain-specific statuses
    RESERVED = "reserved"


class NodeType(str, Enum):
    """Type of compute node."""
    
    COMPUTE = "compute"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"


class SimulationPriority(str, Enum):
    """Priority levels for simulations and scenarios."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"
    
    @classmethod
    def from_common_priority(cls, priority: Priority) -> "SimulationPriority":
        """Convert a common priority to a simulation priority."""
        mapping = {
            Priority.CRITICAL: cls.CRITICAL,
            Priority.HIGH: cls.HIGH,
            Priority.MEDIUM: cls.MEDIUM,
            Priority.LOW: cls.LOW,
            Priority.BACKGROUND: cls.BACKGROUND,
        }
        return mapping.get(priority, cls.MEDIUM)
    
    def to_common_priority(self) -> Priority:
        """Convert a simulation priority to a common priority."""
        mapping = {
            self.CRITICAL: Priority.CRITICAL,
            self.HIGH: Priority.HIGH,
            self.MEDIUM: Priority.MEDIUM,
            self.LOW: Priority.LOW,
            self.BACKGROUND: Priority.BACKGROUND,
        }
        return mapping.get(self, Priority.MEDIUM)


class ComputeNode(BaseNode):
    """Representation of a compute node in the cluster."""

    node_type: NodeType
    network_bandwidth_gbps: float
    current_load: Dict[ResourceType, float] = Field(default_factory=dict)
    assigned_simulations: List[str] = Field(default_factory=list)
    maintenance_window: Optional[Dict[str, datetime]] = None
    location: str
    reliability_score: float = 1.0  # Scale of 0-1, with 1 being most reliable
    
    # For compatibility with BaseNode
    @property
    def assigned_jobs(self) -> List[str]:
        """Alias for assigned_simulations to maintain compatibility with BaseNode."""
        return self.assigned_simulations
    
    @assigned_jobs.setter
    def assigned_jobs(self, value: List[str]):
        """Setter for assigned_jobs that updates assigned_simulations."""
        self.assigned_simulations = value
    
    class Config:
        arbitrary_types_allowed = True


class ClusterStatus:
    """Overall status of the compute cluster."""

    total_nodes: int
    available_nodes: int
    reserved_nodes: int
    maintenance_nodes: int
    offline_nodes: int
    total_resource_usage: Dict[ResourceType, float]
    available_resources: Dict[ResourceType, float]
    running_simulations: int
    queued_simulations: int
    last_updated: datetime = Field(default_factory=datetime.now)
"""Core simulation models and definitions."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field


class ResourceType(str, Enum):
    """Types of resources that can be allocated to simulations."""

    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"


class ResourceRequirement(BaseModel):
    """Resource requirements for a simulation component."""

    resource_type: ResourceType
    amount: float
    unit: str


class SimulationStageStatus(str, Enum):
    """Status of a simulation stage."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationStage(BaseModel):
    """A single stage in a multi-stage simulation workflow."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    estimated_duration: timedelta
    resource_requirements: List[ResourceRequirement] = Field(default_factory=list)
    dependencies: Set[str] = Field(default_factory=set)
    status: SimulationStageStatus = SimulationStageStatus.PENDING
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    checkpoint_frequency: timedelta = Field(default=timedelta(hours=1))
    last_checkpoint_time: Optional[datetime] = None
    checkpoint_path: Optional[str] = None
    error_message: Optional[str] = None


class SimulationPriority(str, Enum):
    """Priority level of a simulation."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


class SimulationStatus(str, Enum):
    """Status of a simulation."""

    DEFINED = "defined"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class Simulation(BaseModel):
    """A complete simulation with multiple stages."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    stages: Dict[str, SimulationStage]
    priority: SimulationPriority = SimulationPriority.MEDIUM
    status: SimulationStatus = SimulationStatus.DEFINED
    creation_time: datetime = Field(default_factory=datetime.now)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    owner: str = "default_owner"
    project: str = "default_project"
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict)
    result_path: Optional[str] = None
    scientific_promise: float = 0.5  # Scale of 0-1 for prioritization
    estimated_total_duration: timedelta = Field(default=timedelta(days=1))
    
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

    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"


class NodeType(str, Enum):
    """Type of compute node."""

    COMPUTE = "compute"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"


class ComputeNode(BaseModel):
    """Representation of a compute node in the cluster."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    node_type: NodeType
    status: NodeStatus = NodeStatus.ONLINE
    cpu_cores: int
    memory_gb: float
    gpu_count: int = 0
    storage_gb: float
    network_bandwidth_gbps: float
    current_load: Dict[ResourceType, float] = Field(default_factory=dict)
    assigned_simulations: List[str] = Field(default_factory=list)
    last_failure_time: Optional[datetime] = None
    maintenance_window: Optional[Dict[str, datetime]] = None
    location: str
    reliability_score: float = 1.0  # Scale of 0-1, with 1 being most reliable
    
    def is_available(self) -> bool:
        """Check if the node is available for new simulations."""
        return self.status == NodeStatus.ONLINE and len(self.assigned_simulations) < self.cpu_cores
    
    def get_available_resources(self) -> Dict[ResourceType, float]:
        """Get the available resources on this node."""
        available = {
            ResourceType.CPU: self.cpu_cores,
            ResourceType.MEMORY: self.memory_gb,
            ResourceType.GPU: self.gpu_count,
            ResourceType.STORAGE: self.storage_gb,
            ResourceType.NETWORK: self.network_bandwidth_gbps
        }
        
        for resource_type, used in self.current_load.items():
            if resource_type in available:
                available[resource_type] -= used
        
        return available
    
    def can_accommodate(self, requirements: List[ResourceRequirement]) -> bool:
        """Check if this node can accommodate the given resource requirements."""
        available = self.get_available_resources()
        
        for req in requirements:
            if req.resource_type not in available:
                return False
            
            if available[req.resource_type] < req.amount:
                return False
        
        return True


class ClusterStatus(BaseModel):
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
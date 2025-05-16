"""
Core models for the unified concurrent task scheduler.

This module defines common base models that are shared between 
the render farm manager and scientific computing implementations.
"""

from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Union, Any, TypeVar, Generic
from uuid import uuid4

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Status values for jobs in both implementations."""
    
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeStatus(str, Enum):
    """Status values for compute/render nodes."""
    
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"
    RESERVED = "reserved"


class Priority(str, Enum):
    """Priority levels for jobs and scenarios."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


class ResourceType(str, Enum):
    """Types of resources that can be allocated to jobs."""
    
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"


class DependencyType(str, Enum):
    """Types of dependencies between jobs or stages."""
    
    SEQUENTIAL = "sequential"  # Must complete in sequence
    DATA = "data"              # Data dependency
    RESOURCE = "resource"      # Resource constraint
    CONDITIONAL = "conditional"  # Depends on a condition
    TIME = "time"              # Time-based dependency


class DependencyState(str, Enum):
    """States for a dependency."""
    
    PENDING = "pending"
    SATISFIED = "satisfied"
    BYPASSED = "bypassed"
    FAILED = "failed"


class LogLevel(str, Enum):
    """Log levels for audit logging."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class CheckpointType(str, Enum):
    """Types of checkpoints."""
    
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    METADATA = "metadata"


class CheckpointStatus(str, Enum):
    """Status values for checkpoints."""
    
    CREATING = "creating"
    COMPLETE = "complete"
    FAILED = "failed"
    ARCHIVED = "archived"
    RESTORING = "restoring"


class ResourceRequirement(BaseModel):
    """Resource requirements for a job or stage."""
    
    resource_type: ResourceType
    amount: float
    unit: str = "units"


class BaseNode(BaseModel):
    """Base model for compute/render nodes."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    status: NodeStatus = NodeStatus.ONLINE
    cpu_cores: int = Field(..., gt=0)
    memory_gb: float = Field(..., gt=0)
    gpu_count: int = Field(default=0, ge=0)
    storage_gb: float = Field(..., gt=0)
    network_bandwidth_gbps: float = Field(default=1.0, gt=0)
    current_load: Dict[ResourceType, float] = Field(default_factory=dict)
    assigned_jobs: List[str] = Field(default_factory=list)
    last_failure_time: Optional[datetime] = None
    uptime_hours: float = Field(default=0, ge=0)
    
    def is_available(self) -> bool:
        """Check if the node is available for new jobs."""
        return self.status == NodeStatus.ONLINE and len(self.assigned_jobs) < self.cpu_cores
    
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


class BaseJob(BaseModel):
    """Base model for render/simulation jobs."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    status: JobStatus = JobStatus.PENDING
    priority: Priority = Priority.MEDIUM
    submission_time: datetime = Field(default_factory=datetime.now)
    estimated_duration: timedelta
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    resource_requirements: List[ResourceRequirement] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    assigned_node_id: Optional[str] = None
    owner: str
    project: str = "default"
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def can_run(self, dependencies_completed: Set[str]) -> bool:
        """Check if the job can run based on its dependencies."""
        return all(dep_id in dependencies_completed for dep_id in self.dependencies)


class Dependency(BaseModel):
    """A dependency between jobs or stages."""
    
    from_id: str
    to_id: str
    dependency_type: DependencyType = DependencyType.SEQUENTIAL
    state: DependencyState = DependencyState.PENDING
    condition: Optional[str] = None
    
    def is_satisfied(self) -> bool:
        """Check if the dependency is satisfied."""
        return self.state in [DependencyState.SATISFIED, DependencyState.BYPASSED]
    
    def satisfy(self) -> None:
        """Mark the dependency as satisfied."""
        self.state = DependencyState.SATISFIED
    
    def bypass(self) -> None:
        """Bypass the dependency."""
        self.state = DependencyState.BYPASSED
    
    def fail(self) -> None:
        """Mark the dependency as failed."""
        self.state = DependencyState.FAILED


class Checkpoint(BaseModel):
    """A checkpoint for a job or simulation."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    checkpoint_type: CheckpointType = CheckpointType.FULL
    status: CheckpointStatus = CheckpointStatus.CREATING
    path: str
    timestamp: datetime = Field(default_factory=datetime.now)
    size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    validation_hash: Optional[str] = None
    restore_count: int = Field(default=0, ge=0)
    last_restore_time: Optional[datetime] = None


# Define a TypeVar for the Result generic type
T = TypeVar('T')

class Result(BaseModel, Generic[T]):
    """Generic result model with success flag and error message."""
    
    success: bool
    value: Optional[T] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, value: Optional[T] = None):
        """Create a successful result."""
        return cls(success=True, value=value)
    
    @classmethod
    def err(cls, error: str):
        """Create a failed result."""
        return cls(success=False, error=error)


class TimeRange(BaseModel):
    """A time range with start and end time."""
    
    start_time: datetime
    end_time: datetime
    
    def contains(self, time: datetime) -> bool:
        """Check if the time is within this time range."""
        return self.start_time <= time <= self.end_time
    
    def overlaps(self, other: "TimeRange") -> bool:
        """Check if this time range overlaps with another."""
        return (self.start_time <= other.end_time and
                other.start_time <= self.end_time)
    
    def duration(self) -> timedelta:
        """Get the duration of this time range."""
        return self.end_time - self.start_time


class AuditLogEntry(BaseModel):
    """Entry in the audit log."""
    
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: str
    job_id: Optional[str] = None
    node_id: Optional[str] = None
    owner_id: Optional[str] = None
    description: str
    details: Dict[str, Any] = Field(default_factory=dict)
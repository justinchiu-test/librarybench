"""Core models for concurrent task scheduling."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, Generic, List, Optional, Set, Tuple, TypeVar, Union
from uuid import uuid4

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field


class JobStatus(str, Enum):
    """Status values for jobs."""
    
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeStatus(str, Enum):
    """Status values for nodes."""
    
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"


class Priority(str, Enum):
    """Priority levels for jobs."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResourceType(str, Enum):
    """Types of resources."""
    
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    SPECIALIZED = "specialized"


class DependencyType(str, Enum):
    """Types of dependencies between jobs or stages."""
    
    SEQUENTIAL = "sequential"  # Must run in sequence
    DATA = "data"  # Depends on data from the other job/stage
    RESOURCE = "resource"  # Depends on resource availability
    CONDITIONAL = "conditional"  # Depends on a condition
    TEMPORAL = "temporal"  # Depends on time-based conditions


class DependencyState(str, Enum):
    """States of dependencies."""
    
    PENDING = "pending"  # Dependency has not been satisfied yet
    SATISFIED = "satisfied"  # Dependency has been satisfied
    FAILED = "failed"  # Dependency has failed
    BYPASSED = "bypassed"  # Dependency has been manually bypassed


class CheckpointType(str, Enum):
    """Types of checkpoints."""
    
    FULL = "full"  # Complete state capture
    INCREMENTAL = "incremental"  # Only changes since last checkpoint
    DELTA = "delta"  # Only differences from baseline
    METADATA = "metadata"  # Only metadata, no actual state


class CheckpointStatus(str, Enum):
    """Status values for checkpoints."""
    
    PENDING = "pending"
    CREATING = "creating"
    COMPLETE = "complete"
    FAILED = "failed"
    RESTORING = "restoring"
    RESTORED = "restored"
    DELETED = "deleted"


class LogLevel(str, Enum):
    """Log levels for auditing and logging."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class BaseModel(PydanticBaseModel):
    """Base model with common functionality."""
    
    class Config:
        """Model configuration."""
        
        arbitrary_types_allowed = True
        orm_mode = True
        
    def model_copy(self, **kwargs):
        """Create a copy of the model."""
        return self.__class__(**{**self.model_dump(), **kwargs})


class ResourceRequirement(BaseModel):
    """Resource requirement for a job or stage."""
    
    resource_type: ResourceType
    amount: float
    unit: str = "unit"
    
    def __hash__(self):
        return hash((self.resource_type, self.amount, self.unit))


class BaseJob(BaseModel):
    """Base job model with common attributes."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    status: JobStatus = JobStatus.PENDING
    priority: Priority = Priority.MEDIUM
    submission_time: datetime = Field(default_factory=datetime.now)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    dependencies: Set[str] = Field(default_factory=set)
    resource_requirements: List[ResourceRequirement] = Field(default_factory=list)
    assigned_node_id: Optional[str] = None
    error_count: int = 0
    progress: float = 0.0
    
    def is_active(self) -> bool:
        """Check if the job is active."""
        return self.status in [JobStatus.RUNNING, JobStatus.QUEUED]
    
    def is_complete(self) -> bool:
        """Check if the job is complete."""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    def get_duration(self) -> Optional[timedelta]:
        """Get the duration of the job."""
        if not self.start_time:
            return None
        
        end = self.end_time or datetime.now()
        return end - self.start_time


class BaseNode(BaseModel):
    """Base node model with common attributes."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    status: NodeStatus = NodeStatus.OFFLINE
    current_job_id: Optional[str] = None
    resources: Dict[ResourceType, float] = Field(default_factory=dict)
    uptime_hours: float = 0.0
    last_error: Optional[str] = None
    
    def is_available(self) -> bool:
        """Check if the node is available for jobs."""
        return self.status == NodeStatus.ONLINE and self.current_job_id is None
    
    def is_busy(self) -> bool:
        """Check if the node is busy."""
        return self.status == NodeStatus.ONLINE and self.current_job_id is not None
    
    def can_satisfy_requirements(self, requirements: List[ResourceRequirement]) -> bool:
        """Check if the node can satisfy the resource requirements."""
        for req in requirements:
            if req.resource_type not in self.resources:
                return False
            
            if self.resources[req.resource_type] < req.amount:
                return False
        
        return True


class Dependency(BaseModel):
    """Dependency between jobs or stages."""
    
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
    
    def fail(self) -> None:
        """Mark the dependency as failed."""
        self.state = DependencyState.FAILED
    
    def bypass(self) -> None:
        """Bypass the dependency."""
        self.state = DependencyState.BYPASSED
    
    # Aliases for compatibility with tests
    @property
    def from_stage_id(self) -> str:
        """Alias for from_id to be compatible with stage-based tests."""
        return self.from_id
    
    @property
    def to_stage_id(self) -> str:
        """Alias for to_id to be compatible with stage-based tests."""
        return self.to_id


class Checkpoint(BaseModel):
    """Checkpoint for a job or stage."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    checkpoint_type: CheckpointType = CheckpointType.FULL
    status: CheckpointStatus = CheckpointStatus.PENDING
    timestamp: datetime = Field(default_factory=datetime.now)
    path: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def is_complete(self) -> bool:
        """Check if the checkpoint is complete."""
        return self.status == CheckpointStatus.COMPLETE
    
    def is_restorable(self) -> bool:
        """Check if the checkpoint can be restored."""
        return self.status in [CheckpointStatus.COMPLETE, CheckpointStatus.RESTORED]


class AuditLogEntry(BaseModel):
    """Audit log entry for tracking operations."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: str
    level: LogLevel = LogLevel.INFO
    job_id: Optional[str] = None
    node_id: Optional[str] = None
    user_id: Optional[str] = None
    description: str
    details: Dict[str, Any] = Field(default_factory=dict)


class TimeRange(BaseModel):
    """Time range for scheduling and reporting."""
    
    start: datetime
    end: datetime
    
    def duration(self) -> timedelta:
        """Get the duration of the time range."""
        return self.end - self.start
    
    def contains(self, time: datetime) -> bool:
        """Check if the time range contains the given time."""
        return self.start <= time <= self.end
    
    def overlaps(self, other: TimeRange) -> bool:
        """Check if this time range overlaps with another."""
        return (self.start <= other.end) and (other.start <= self.end)


T = TypeVar('T')


class Result(Generic[T]):
    """Generic result type for operations that can succeed or fail."""
    
    def __init__(self, success: bool, value: Optional[T] = None, error: Optional[str] = None):
        self.success = success
        self.value = value
        self.error = error
    
    @classmethod
    def ok(cls, value: T) -> Result[T]:
        """Create a successful result."""
        return cls(True, value)
    
    @classmethod
    def err(cls, error: str) -> Result[T]:
        """Create a failed result."""
        return cls(False, error=error)
    
    def unwrap(self) -> T:
        """Get the value or raise an exception if the result is an error."""
        if not self.success:
            raise ValueError(f"Cannot unwrap error result: {self.error}")
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        """Get the value or a default if the result is an error."""
        if not self.success:
            return default
        return self.value
    
    def map(self, f: callable) -> Result:
        """Apply a function to the value if the result is successful."""
        if not self.success:
            return self
        return Result.ok(f(self.value))
    
    def __bool__(self) -> bool:
        """Convert to boolean."""
        return self.success
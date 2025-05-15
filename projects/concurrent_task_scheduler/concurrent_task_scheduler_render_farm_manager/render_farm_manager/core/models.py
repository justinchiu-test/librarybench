"""Core models for the Render Farm Manager."""

from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Union
from pydantic import BaseModel, Field


class JobPriority(str, Enum):
    """Priority levels for render jobs."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RenderJobStatus(str, Enum):
    """Status values for render jobs."""
    
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeStatus(str, Enum):
    """Status values for render nodes."""
    
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"


class EnergyMode(str, Enum):
    """Energy usage modes for the render farm."""
    
    PERFORMANCE = "performance"  # Maximum performance, disregard energy usage
    BALANCED = "balanced"  # Balance between performance and energy efficiency
    EFFICIENCY = "efficiency"  # Optimize for energy efficiency, may impact performance
    NIGHT_SAVINGS = "night_savings"  # Special mode for overnight operations


class NodeCapabilities(BaseModel):
    """Capabilities and specifications of a render node."""
    
    cpu_cores: int = Field(..., gt=0)
    memory_gb: int = Field(..., gt=0)
    gpu_model: Optional[str] = None
    gpu_count: int = Field(default=0, ge=0)
    gpu_memory_gb: float = Field(default=0, ge=0)
    gpu_compute_capability: float = Field(default=0, ge=0)
    storage_gb: int = Field(..., gt=0)
    specialized_for: List[str] = Field(default_factory=list)


class RenderNode(BaseModel):
    """A node in the render farm capable of executing render jobs."""
    
    id: str
    name: str
    status: str
    capabilities: NodeCapabilities
    power_efficiency_rating: float = Field(..., ge=0, le=100)
    current_job_id: Optional[str] = None
    performance_history: Dict[str, float] = Field(default_factory=dict)
    last_error: Optional[str] = None
    uptime_hours: float = Field(default=0, ge=0)
    
    def model_copy(self, **kwargs):
        """Create a copy of the model."""
        return self.__class__(**{**self.model_dump(), **kwargs})
    
    def copy(self, **kwargs):
        """Deprecated copy method."""
        return self.model_copy(**kwargs)


class RenderJob(BaseModel):
    """A rendering job submitted to the farm."""
    
    id: str
    name: str
    client_id: str
    status: RenderJobStatus = RenderJobStatus.PENDING
    job_type: str
    priority: JobPriority
    submission_time: datetime
    deadline: datetime
    estimated_duration_hours: float = Field(..., gt=0)
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    requires_gpu: bool = False
    memory_requirements_gb: int = Field(..., gt=0)
    cpu_requirements: int = Field(..., gt=0)
    scene_complexity: int = Field(..., ge=1, le=10)
    dependencies: List[str] = Field(default_factory=list)
    assigned_node_id: Optional[str] = None
    output_path: str
    error_count: int = Field(default=0, ge=0)
    can_be_preempted: bool = True
    supports_progressive_output: bool = False
    last_checkpoint_time: Optional[datetime] = None
    last_progressive_output_time: Optional[datetime] = None
    
    def model_copy(self, **kwargs):
        """Create a copy of the model."""
        return self.__class__(**{**self.model_dump(), **kwargs})
    
    def copy(self, **kwargs):
        """Deprecated copy method."""
        return self.model_copy(**kwargs)


class Client(BaseModel):
    """A client organization that submits render jobs to the farm."""
    
    id: str
    name: str
    sla_tier: str  # premium, standard, basic
    guaranteed_resources: int = Field(..., ge=0)  # Percentage of resources guaranteed
    max_resources: int = Field(..., ge=0)  # Maximum percentage of resources allowed


class ProgressiveOutputConfig(BaseModel):
    """Configuration for progressive result generation."""
    
    enabled: bool = True
    interval_minutes: int = Field(default=30, gt=0)
    quality_levels: List[int] = Field(default_factory=lambda: [25, 50, 75])
    max_overhead_percentage: float = Field(default=5.0, ge=0.0, le=100.0)


class ResourceAllocation(BaseModel):
    """Resource allocation for a specific client."""
    
    client_id: str
    allocated_percentage: float = Field(..., ge=0, le=100)
    allocated_nodes: List[str] = Field(default_factory=list)
    borrowed_percentage: float = Field(default=0, ge=0)
    borrowed_from: Dict[str, float] = Field(default_factory=dict)
    lent_percentage: float = Field(default=0, ge=0)
    lent_to: Dict[str, float] = Field(default_factory=dict)


class PerformanceMetrics(BaseModel):
    """Performance metrics for the render farm."""
    
    total_jobs_completed: int = 0
    jobs_completed_on_time: int = 0
    average_utilization_percentage: float = 0.0
    average_node_idle_percentage: float = 0.0
    energy_usage_kwh: float = 0.0
    average_job_turnaround_hours: float = 0.0
    preemptions_count: int = 0
    node_failures_count: int = 0
    optimization_improvement_percentage: float = 0.0


class AuditLogEntry(BaseModel):
    """Entry in the audit log for the render farm."""
    
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: str
    job_id: Optional[str] = None
    node_id: Optional[str] = None
    client_id: Optional[str] = None
    description: str
    details: Dict = Field(default_factory=dict)
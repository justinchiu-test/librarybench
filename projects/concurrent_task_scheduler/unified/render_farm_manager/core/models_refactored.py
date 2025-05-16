"""Refactored core models for the Render Farm Manager."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Union
from pydantic import Field

from common.core.models import (
    BaseJob, 
    BaseModel, 
    BaseNode,
    JobStatus,
    LogLevel,
    NodeStatus,
    Priority,
    ResourceRequirement,
    ResourceType,
)


class ServiceTier(str, Enum):
    """Service tiers for clients."""
    
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class NodeType(str, Enum):
    """Types of render nodes."""
    
    CPU = "cpu"
    GPU = "gpu"
    HYBRID = "hybrid"
    SPECIALIZED = "specialized"


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


class RenderNode(BaseNode):
    """A node in the render farm capable of executing render jobs."""
    
    capabilities: NodeCapabilities
    power_efficiency_rating: float = Field(..., ge=0, le=100)
    performance_history: Dict[str, float] = Field(default_factory=dict)
    
    def get_resource_value(self, resource_type: ResourceType) -> float:
        """Get the value of a specific resource type."""
        if resource_type == ResourceType.CPU:
            return self.capabilities.cpu_cores
        elif resource_type == ResourceType.MEMORY:
            return self.capabilities.memory_gb
        elif resource_type == ResourceType.GPU:
            return self.capabilities.gpu_count
        elif resource_type == ResourceType.STORAGE:
            return self.capabilities.storage_gb
        else:
            return 0.0
    
    def convert_to_resources_dict(self) -> Dict[ResourceType, float]:
        """Convert node capabilities to a resources dictionary for BaseNode."""
        resources = {
            ResourceType.CPU: self.capabilities.cpu_cores,
            ResourceType.MEMORY: self.capabilities.memory_gb,
            ResourceType.STORAGE: self.capabilities.storage_gb,
        }
        
        if self.capabilities.gpu_count > 0:
            resources[ResourceType.GPU] = self.capabilities.gpu_count
            
        if self.capabilities.specialized_for:
            resources[ResourceType.SPECIALIZED] = 1.0
            
        return resources
        
    def update_base_fields(self) -> None:
        """Update base class fields based on this class's fields."""
        self.resources = self.convert_to_resources_dict()


class RenderJob(BaseJob):
    """A rendering job submitted to the farm."""
    
    client_id: str
    job_type: str
    deadline: datetime
    estimated_duration_hours: float = Field(..., gt=0)
    requires_gpu: bool = False
    memory_requirements_gb: int = Field(..., gt=0)
    cpu_requirements: int = Field(..., gt=0)
    scene_complexity: int = Field(..., ge=1, le=10)
    output_path: str
    can_be_preempted: bool = True
    supports_progressive_output: bool = False
    supports_checkpoint: bool = False
    last_checkpoint_time: Optional[datetime] = None
    last_progressive_output_time: Optional[datetime] = None
    energy_intensive: bool = False
    
    def convert_to_resource_requirements(self) -> List[ResourceRequirement]:
        """Convert job requirements to ResourceRequirement list."""
        requirements = [
            ResourceRequirement(
                resource_type=ResourceType.CPU,
                amount=self.cpu_requirements,
                unit="cores"
            ),
            ResourceRequirement(
                resource_type=ResourceType.MEMORY,
                amount=self.memory_requirements_gb,
                unit="GB"
            ),
        ]
        
        if self.requires_gpu:
            requirements.append(
                ResourceRequirement(
                    resource_type=ResourceType.GPU,
                    amount=1,
                    unit="device"
                )
            )
            
        return requirements
        
    def update_base_fields(self) -> None:
        """Update base class fields based on this class's fields."""
        self.resource_requirements = self.convert_to_resource_requirements()
        
    def elapsed_time(self) -> float:
        """Get the elapsed time since job submission in hours."""
        if not self.submission_time:
            return 0.0
        
        now = datetime.now()
        return (now - self.submission_time).total_seconds() / 3600
        
    def time_to_deadline(self) -> float:
        """Get the time remaining until the deadline in hours."""
        if not self.deadline:
            return float('inf')
        
        now = datetime.now()
        if now > self.deadline:
            return 0.0
        
        return (self.deadline - now).total_seconds() / 3600
        
    def is_at_risk(self) -> bool:
        """Check if the job is at risk of missing its deadline."""
        if not self.deadline or self.is_complete():
            return False
        
        remaining_time = self.time_to_deadline()
        estimated_completion_time = self.estimated_duration_hours * (1 - self.progress / 100)
        
        return remaining_time < estimated_completion_time * 1.1  # 10% safety margin


class Client(BaseModel):
    """A client organization that submits render jobs to the farm."""
    
    id: str
    name: str
    sla_tier: str  # premium, standard, basic
    guaranteed_resources: int = Field(..., ge=0)  # Percentage of resources guaranteed
    max_resources: int = Field(..., ge=0)  # Maximum percentage of resources allowed


class RenderClient(BaseModel):
    """A client organization that submits render jobs to the farm."""
    
    client_id: str
    name: str
    service_tier: ServiceTier
    guaranteed_resources: int = Field(default=0, ge=0)  # Percentage of resources guaranteed
    max_resources: int = Field(default=100, ge=0)  # Maximum percentage of resources allowed
    
    @property
    def id(self) -> str:
        """Get the client ID (alias for client_id for compatibility)."""
        return self.client_id
    
    @property
    def sla_tier(self) -> str:
        """Get the SLA tier (alias for service_tier for compatibility)."""
        return self.service_tier


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
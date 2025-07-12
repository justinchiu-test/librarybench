"""Data models for Kubernetes resource monitoring."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class ResourceType(str, Enum):
    """Types of Kubernetes resources."""

    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    EPHEMERAL_STORAGE = "ephemeral-storage"


class OptimizationTarget(str, Enum):
    """Resource optimization targets."""

    BALANCED = "balanced"
    PERFORMANCE = "performance"
    COST = "cost"


class MetricType(str, Enum):
    """Types of metrics for HPA."""

    RESOURCE = "resource"
    CUSTOM = "custom"
    REQUESTS_PER_SECOND = "requests_per_second"
    RESPONSE_TIME = "response_time"
    QUEUE_DEPTH = "queue_depth"


class AggregationType(str, Enum):
    """Metric aggregation types."""

    AVG = "avg"
    MAX = "max"
    MIN = "min"
    P50 = "p50"
    P90 = "p90"
    P95 = "p95"
    P99 = "p99"


class ContainerStats(BaseModel):
    """Container resource statistics."""

    name: str
    container_id: str
    runtime: str = Field(
        ..., description="Container runtime (docker, containerd, cri-o)"
    )
    cpu_usage: float = Field(..., description="CPU usage in millicores")
    cpu_limit: Optional[float] = Field(None, description="CPU limit in millicores")
    cpu_request: Optional[float] = Field(None, description="CPU request in millicores")
    memory_usage: int = Field(..., description="Memory usage in bytes")
    memory_limit: Optional[int] = Field(None, description="Memory limit in bytes")
    memory_request: Optional[int] = Field(None, description="Memory request in bytes")
    restart_count: int = 0
    is_oomkilled: bool = False
    cgroup_path: str = ""


class PodResources(BaseModel):
    """Pod resource information."""

    name: str
    namespace: str
    uid: str
    node_name: str
    phase: str
    containers: List[ContainerStats]
    total_cpu_usage: float = 0
    total_cpu_limit: Optional[float] = None
    total_cpu_request: Optional[float] = None
    total_memory_usage: int = 0
    total_memory_limit: Optional[int] = None
    total_memory_request: Optional[int] = None
    has_resource_limits: bool = True
    is_shared_process_namespace: bool = False
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

    def calculate_efficiency(self) -> Dict[str, float]:
        """Calculate resource utilization efficiency."""
        efficiency = {}

        if self.total_cpu_request and self.total_cpu_request > 0:
            efficiency["cpu"] = self.total_cpu_usage / self.total_cpu_request

        if self.total_memory_request and self.total_memory_request > 0:
            efficiency["memory"] = self.total_memory_usage / self.total_memory_request

        return efficiency


class ResourceBreach(BaseModel):
    """Resource limit breach detection."""

    model_config = ConfigDict(validate_assignment=True)

    pod_name: str
    namespace: str
    container_name: str
    resource_type: ResourceType
    current_usage: float
    limit: float
    threshold_percent: float
    breach_percent: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
    severity: str = "warning"

    def model_post_init(self, __context: Any) -> None:
        """Calculate breach percent and severity after initialization."""
        self.breach_percent = (self.current_usage / self.limit) * 100
        if self.breach_percent >= 95:
            self.severity = "critical"
        elif self.breach_percent >= 90:
            self.severity = "warning"
        else:
            self.severity = "info"


class NodePressure(BaseModel):
    """Node resource pressure information."""

    node_name: str
    cpu_capacity: float
    cpu_allocatable: float
    cpu_allocated: float
    cpu_usage: float
    memory_capacity: int
    memory_allocatable: int
    memory_allocated: int
    memory_usage: int
    ephemeral_storage_capacity: int
    ephemeral_storage_allocatable: int
    ephemeral_storage_usage: int
    pod_capacity: int
    pod_count: int
    conditions: Dict[str, bool] = Field(default_factory=dict)
    scheduling_pressure: float = 0
    eviction_risk: float = 0
    resource_fragmentation: float = 0
    timestamp: datetime = Field(default_factory=datetime.now)

    def calculate_pressure_metrics(self) -> None:
        """Calculate scheduling pressure and eviction risk."""
        cpu_pressure = (
            self.cpu_allocated / self.cpu_allocatable if self.cpu_allocatable > 0 else 0
        )
        memory_pressure = (
            self.memory_allocated / self.memory_allocatable
            if self.memory_allocatable > 0
            else 0
        )
        pod_pressure = (
            self.pod_count / self.pod_capacity if self.pod_capacity > 0 else 0
        )

        self.scheduling_pressure = max(cpu_pressure, memory_pressure, pod_pressure)

        # Calculate eviction risk based on actual usage
        cpu_usage_ratio = (
            self.cpu_usage / self.cpu_allocatable if self.cpu_allocatable > 0 else 0
        )
        memory_usage_ratio = (
            self.memory_usage / self.memory_allocatable
            if self.memory_allocatable > 0
            else 0
        )

        self.eviction_risk = max(cpu_usage_ratio, memory_usage_ratio)

        # Calculate fragmentation (difference between allocated and used)
        if self.cpu_allocated > 0:
            cpu_frag = 1 - (self.cpu_usage / self.cpu_allocated)
        else:
            cpu_frag = 0

        if self.memory_allocated > 0:
            memory_frag = 1 - (self.memory_usage / self.memory_allocated)
        else:
            memory_frag = 0

        self.resource_fragmentation = (cpu_frag + memory_frag) / 2


class HPAMetric(BaseModel):
    """Horizontal Pod Autoscaler metric."""

    deployment: str
    namespace: str
    metric_type: MetricType
    metric_name: str
    value: float
    aggregation: AggregationType
    window: str = "1m"
    timestamp: datetime = Field(default_factory=datetime.now)
    target_value: Optional[float] = None
    min_replicas: int = 1
    max_replicas: int = 10
    current_replicas: int = 1
    desired_replicas: Optional[int] = None

    def calculate_desired_replicas(self) -> int:
        """Calculate desired replicas based on metric value and target."""
        if not self.target_value or self.target_value <= 0:
            return self.current_replicas

        ratio = self.value / self.target_value
        desired = int(self.current_replicas * ratio)

        # Ensure within bounds
        desired = max(self.min_replicas, min(desired, self.max_replicas))
        self.desired_replicas = desired

        return desired


class ResourceQuota(BaseModel):
    """Namespace resource quota information."""

    namespace: str
    quota_name: str
    hard_limits: Dict[str, str] = Field(default_factory=dict)
    used: Dict[str, str] = Field(default_factory=dict)
    utilization: Dict[str, float] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

    def calculate_utilization(self) -> None:
        """Calculate quota utilization percentages."""
        for resource, limit in self.hard_limits.items():
            if resource in self.used:
                try:
                    limit_val = self._parse_resource_value(limit)
                    used_val = self._parse_resource_value(self.used[resource])
                    if limit_val > 0:
                        self.utilization[resource] = (used_val / limit_val) * 100
                except Exception:
                    self.utilization[resource] = 0

    @staticmethod
    def _parse_resource_value(value: str) -> float:
        """Parse Kubernetes resource values (e.g., '100m', '2Gi')."""
        if not value:
            return 0

        value = str(value).strip()

        # Handle CPU values
        if value.endswith("m"):
            return float(value[:-1])
        elif value.endswith("n"):
            return float(value[:-1]) / 1_000_000

        # Handle memory values
        multipliers = {
            "Ki": 1024,
            "Mi": 1024**2,
            "Gi": 1024**3,
            "Ti": 1024**4,
            "K": 1000,
            "M": 1000**2,
            "G": 1000**3,
            "T": 1000**4,
        }

        for suffix, multiplier in multipliers.items():
            if value.endswith(suffix):
                return float(value[: -len(suffix)]) * multiplier

        # Plain number
        return float(value)


class NamespaceResources(BaseModel):
    """Namespace resource statistics."""

    namespace: str
    pods: List[PodResources] = Field(default_factory=list)
    quotas: List[ResourceQuota] = Field(default_factory=list)
    total_cpu_usage: float = 0
    total_cpu_request: float = 0
    total_cpu_limit: float = 0
    total_memory_usage: int = 0
    total_memory_request: int = 0
    total_memory_limit: int = 0
    pod_count: int = 0
    container_count: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)

    def calculate_totals(self) -> None:
        """Calculate total resource usage across all pods."""
        self.pod_count = len(self.pods)
        self.container_count = sum(len(pod.containers) for pod in self.pods)

        self.total_cpu_usage = sum(pod.total_cpu_usage for pod in self.pods)
        self.total_cpu_request = sum(pod.total_cpu_request or 0 for pod in self.pods)
        self.total_cpu_limit = sum(pod.total_cpu_limit or 0 for pod in self.pods)

        self.total_memory_usage = sum(pod.total_memory_usage for pod in self.pods)
        self.total_memory_request = sum(
            pod.total_memory_request or 0 for pod in self.pods
        )
        self.total_memory_limit = sum(pod.total_memory_limit or 0 for pod in self.pods)


class ResourceRecommendation(BaseModel):
    """Resource recommendation for optimization."""

    namespace: str
    pod_name: str
    container_name: str
    resource_type: ResourceType
    current_request: Optional[float]
    current_limit: Optional[float]
    recommended_request: float
    recommended_limit: float
    optimization_target: OptimizationTarget
    reason: str
    potential_savings: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)

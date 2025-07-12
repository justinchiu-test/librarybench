"""Data models for PyMockAPI microservices."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, field_validator


class ServiceStatus(str, Enum):
    """Service health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ChaosScenario(str, Enum):
    """Types of chaos scenarios."""
    SERVICE_DOWN = "service_down"
    NETWORK_LATENCY = "network_latency"
    NETWORK_PARTITION = "network_partition"
    RESPONSE_ERROR = "response_error"
    CASCADE_FAILURE = "cascade_failure"


class ServiceMetadata(BaseModel):
    """Service metadata for registry."""
    service_id: str
    name: str
    version: str = "1.0.0"
    endpoint: str
    port: int
    status: ServiceStatus = ServiceStatus.HEALTHY
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    health_check_url: Optional[str] = None
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v


class ServiceDependency(BaseModel):
    """Represents a dependency between services."""
    from_service: str
    to_service: str
    required: bool = True
    timeout_ms: int = 5000
    retry_count: int = 3
    circuit_breaker_enabled: bool = True
    
    @field_validator('timeout_ms')
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Timeout must be non-negative")
        return v


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: int = 60
    half_open_max_requests: int = 3
    
    @field_validator('failure_threshold', 'success_threshold', 'half_open_max_requests')
    @classmethod
    def validate_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Value must be positive")
        return v


class TraceContext(BaseModel):
    """W3C Trace Context representation."""
    trace_id: str
    parent_id: Optional[str] = None
    span_id: str
    trace_flags: str = "01"
    trace_state: Optional[str] = None
    
    @field_validator('trace_id')
    @classmethod
    def validate_trace_id(cls, v: str) -> str:
        if len(v) != 32 or not all(c in '0123456789abcdef' for c in v.lower()):
            raise ValueError("trace_id must be 32 hex characters")
        return v.lower()
    
    @field_validator('span_id')
    @classmethod
    def validate_span_id(cls, v: str) -> str:
        if len(v) != 16 or not all(c in '0123456789abcdef' for c in v.lower()):
            raise ValueError("span_id must be 16 hex characters")
        return v.lower()


class Span(BaseModel):
    """Distributed tracing span."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    service_name: str
    operation_name: str
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    tags: Dict[str, Any] = Field(default_factory=dict)
    status_code: int = 200
    error: Optional[str] = None


class ChaosEvent(BaseModel):
    """Chaos engineering event."""
    event_id: str
    scenario: ChaosScenario
    target_services: List[str]
    duration_seconds: Optional[int] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    active: bool = True


class ServiceGraph(BaseModel):
    """Service dependency graph representation."""
    services: List[ServiceMetadata]
    dependencies: List[ServiceDependency]
    
    def get_dependencies_for_service(self, service_id: str) -> List[ServiceDependency]:
        """Get all dependencies for a service."""
        return [dep for dep in self.dependencies if dep.from_service == service_id]
    
    def get_dependents_of_service(self, service_id: str) -> List[ServiceDependency]:
        """Get all services that depend on this service."""
        return [dep for dep in self.dependencies if dep.to_service == service_id]
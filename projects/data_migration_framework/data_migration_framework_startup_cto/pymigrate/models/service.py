"""Service-related models for PyMigrate."""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Set
from pydantic import BaseModel, Field, validator


class HTTPMethod(str, Enum):
    """HTTP methods for API endpoints."""
    
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ServiceType(str, Enum):
    """Types of microservices."""
    
    USER = "user"
    ORDER = "order"
    INVENTORY = "inventory"
    PAYMENT = "payment"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"
    CUSTOM = "custom"


class RoutingStrategy(str, Enum):
    """Traffic routing strategies."""
    
    PERCENTAGE = "percentage"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    FEATURE_FLAG = "feature_flag"


class ServiceBoundary(BaseModel):
    """Represents a proposed service boundary."""
    
    service_name: str
    service_type: ServiceType
    tables: List[str]
    relationships: Dict[str, List[str]] = Field(default_factory=dict)
    access_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_size_mb: float
    transaction_boundaries: List[str] = Field(default_factory=list)
    dependencies: Set[str] = Field(default_factory=set)
    confidence_score: float = Field(ge=0.0, le=1.0)
    
    @validator("tables")
    def validate_tables(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Service boundary must include at least one table")
        return v


class APIEndpoint(BaseModel):
    """Generated API endpoint specification."""
    
    path: str
    method: HTTPMethod
    description: str
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    query_parameters: List[Dict[str, Any]] = Field(default_factory=list)
    headers: Dict[str, str] = Field(default_factory=dict)
    authentication_required: bool = True
    rate_limit: Optional[int] = None
    openapi_spec: Dict[str, Any] = Field(default_factory=dict)
    
    @validator("path")
    def validate_path(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("API path must start with /")
        return v


class RouteConfig(BaseModel):
    """Configuration for traffic routing."""
    
    service_name: str
    strategy: RoutingStrategy
    percentage: float = Field(ge=0.0, le=100.0)
    sticky_sessions: bool = False
    health_check_interval_ms: int = Field(default=5000, ge=1000)
    failover_threshold: int = Field(default=3, ge=1)
    rollback_enabled: bool = True
    feature_flags: Dict[str, bool] = Field(default_factory=dict)
    
    @validator("percentage")
    def validate_percentage(cls, v: float, values: Dict[str, Any]) -> float:
        if values.get("strategy") == RoutingStrategy.PERCENTAGE and not (0 <= v <= 100):
            raise ValueError("Percentage must be between 0 and 100")
        return v


class TrafficDistribution(BaseModel):
    """Current traffic distribution across services."""
    
    timestamp: datetime
    distributions: Dict[str, float] = Field(default_factory=dict)
    total_requests: int = 0
    success_rate: float = Field(ge=0.0, le=100.0)
    average_latency_ms: float
    error_counts: Dict[str, int] = Field(default_factory=dict)
    active_routes: List[RouteConfig] = Field(default_factory=list)
    
    @validator("distributions")
    def validate_distributions(cls, v: Dict[str, float]) -> Dict[str, float]:
        total = sum(v.values())
        if total > 0 and abs(total - 100.0) > 0.01:
            raise ValueError("Traffic distributions must sum to 100%")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
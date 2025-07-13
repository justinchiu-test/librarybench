"""Configuration models for PyMigrate."""

from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator


class ConflictResolutionStrategy(str, Enum):
    """Strategies for resolving data conflicts during bi-directional sync."""
    
    LAST_WRITE_WINS = "last_write_wins"
    PRIORITY_BASED = "priority_based"
    CUSTOM = "custom"
    MANUAL = "manual"


class DatabaseType(str, Enum):
    """Supported database types."""
    
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"


class DatabaseConfig(BaseModel):
    """Database connection configuration."""
    
    type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str
    options: Dict[str, Any] = Field(default_factory=dict)
    
    @validator("port")
    def validate_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v


class ServiceConfig(BaseModel):
    """Microservice configuration."""
    
    name: str
    version: str = "1.0.0"
    base_url: str
    health_check_path: str = "/health"
    timeout: int = Field(default=30, ge=1, le=300)
    retry_count: int = Field(default=3, ge=0, le=10)
    
    @validator("base_url")
    def validate_base_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return v.rstrip("/")


class SyncConfig(BaseModel):
    """Configuration for bi-directional synchronization."""
    
    source_db: DatabaseConfig
    target_db: DatabaseConfig
    conflict_resolution: ConflictResolutionStrategy = ConflictResolutionStrategy.LAST_WRITE_WINS
    sync_interval_ms: int = Field(default=100, ge=10, le=60000)
    batch_size: int = Field(default=1000, ge=1, le=10000)
    max_retries: int = Field(default=3, ge=0, le=10)
    enable_audit_log: bool = True
    priority_rules: Optional[Dict[str, int]] = None
    custom_resolver: Optional[str] = None
    
    @validator("custom_resolver")
    def validate_custom_resolver(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        if v and values.get("conflict_resolution") != ConflictResolutionStrategy.CUSTOM:
            raise ValueError("custom_resolver requires conflict_resolution to be CUSTOM")
        return v
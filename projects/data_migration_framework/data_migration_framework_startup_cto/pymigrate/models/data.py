"""Data models for PyMigrate."""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    """Types of data changes."""
    
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


class SyncDirection(str, Enum):
    """Direction of synchronization."""
    
    SOURCE_TO_TARGET = "source_to_target"
    TARGET_TO_SOURCE = "target_to_source"
    BIDIRECTIONAL = "bidirectional"


class SyncState(str, Enum):
    """State of synchronization."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class DataChange(BaseModel):
    """Represents a data change event."""
    
    id: str
    table_name: str
    change_type: ChangeType
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source_system: str
    checksum: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConflictReport(BaseModel):
    """Report of a data conflict during synchronization."""
    
    id: str
    table_name: str
    record_id: str
    source_change: DataChange
    target_change: DataChange
    detected_at: datetime
    resolution_strategy: str
    resolved: bool = False
    resolution_details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SyncStatus(BaseModel):
    """Status of a synchronization operation."""
    
    sync_id: str
    direction: SyncDirection
    state: SyncState
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    records_synced: int = 0
    conflicts_detected: int = 0
    errors: List[str] = Field(default_factory=list)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConsistencyReport(BaseModel):
    """Report of data consistency validation."""
    
    validation_id: str
    timestamp: datetime
    tables_checked: List[str]
    total_records: int
    consistent_records: int
    inconsistent_records: int
    discrepancies: List[Dict[str, Any]] = Field(default_factory=list)
    validation_duration_ms: int
    checksum_mismatches: List[Dict[str, Any]] = Field(default_factory=list)
    
    @property
    def consistency_percentage(self) -> float:
        """Calculate consistency percentage."""
        if self.total_records == 0:
            return 100.0
        return (self.consistent_records / self.total_records) * 100
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
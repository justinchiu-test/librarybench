"""Enum definitions for the unified task manager CLI."""

from enum import Enum


class TaskStatusEnum(str, Enum):
    """Common status values for tasks across all implementations."""
    
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskPriorityEnum(str, Enum):
    """Common priority levels for tasks across all implementations."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
"""Base models for the unified task manager library.

This module provides shared base models that can be extended by persona-specific
implementations, ensuring consistent behavior and reducing code duplication.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Union, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, root_validator


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


class BaseEntity(BaseModel):
    """Base model for all entities with common fields and methods."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def update(self, **kwargs) -> None:
        """
        Update entity fields with the provided values.
        
        Args:
            **kwargs: Field-value pairs to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
        
    class Config:
        json_encoders = {
            UUID: str  # Ensure UUIDs are serialized as strings
        }


class BaseTask(BaseEntity):
    """
    Base model for tasks with common fields and methods.
    
    This model provides the foundation for task-related entities across
    different persona implementations, with shared fields and behavior.
    """
    
    title: str
    description: str
    status: str
    priority: str
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Organizational attributes
    tags: Set[str] = Field(default_factory=set)
    notes: List[str] = Field(default_factory=list)
    
    # Task relationships
    parent_id: Optional[str] = None
    subtask_ids: Set[str] = Field(default_factory=set)
    
    # Custom metadata for extensibility
    custom_metadata: Dict[str, Union[str, int, float, bool, list, dict]] = Field(
        default_factory=dict
    )
    
    def update(self, **kwargs) -> None:
        """
        Update task fields with the provided values.
        
        This method extends the base update method to handle completion status.
        
        Args:
            **kwargs: Field-value pairs to update
        """
        super().update(**kwargs)
        
        # Update completion timestamp if status changed to completed
        if self.status == "completed" and not self.completed_at:
            self.completed_at = datetime.now()
    
    def add_note(self, note: str) -> None:
        """
        Add a note to the task.
        
        Args:
            note: The note content to add
        """
        self.notes.append(note)
        self.updated_at = datetime.now()
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the task.
        
        Args:
            tag: The tag to add
        """
        self.tags.add(tag)
        self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str) -> bool:
        """
        Remove a tag from the task.
        
        Args:
            tag: The tag to remove
            
        Returns:
            bool: True if tag was removed, False if not found
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
            return True
        return False
    
    def add_subtask(self, subtask_id: Union[str, UUID]) -> None:
        """
        Add a subtask to this task.
        
        Args:
            subtask_id: ID of the subtask
        """
        # Convert UUID to string if needed
        if isinstance(subtask_id, UUID):
            subtask_id = str(subtask_id)
            
        self.subtask_ids.add(subtask_id)
        self.updated_at = datetime.now()
    
    def remove_subtask(self, subtask_id: Union[str, UUID]) -> bool:
        """
        Remove a subtask from this task.
        
        Args:
            subtask_id: ID of the subtask to remove
            
        Returns:
            bool: True if subtask was removed, False if not found
        """
        # Convert UUID to string if needed
        if isinstance(subtask_id, UUID):
            subtask_id = str(subtask_id)
            
        if subtask_id in self.subtask_ids:
            self.subtask_ids.remove(subtask_id)
            self.updated_at = datetime.now()
            return True
        return False
    
    def update_custom_metadata(self, key: str, value: Union[str, int, float, bool, list, dict]) -> None:
        """
        Update a custom metadata field.
        
        Args:
            key: The metadata key
            value: The metadata value
        """
        self.custom_metadata[key] = value
        self.updated_at = datetime.now()
    
    def remove_custom_metadata(self, key: str) -> bool:
        """
        Remove a custom metadata field.
        
        Args:
            key: The key of the custom field to remove
            
        Returns:
            bool: True if field was removed, False if not found
        """
        if key in self.custom_metadata:
            del self.custom_metadata[key]
            self.updated_at = datetime.now()
            return True
        return False
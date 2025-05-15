"""
Task manager implementation that combines functionality from both 
researcher and security analyst personas.
"""

from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Set, Union, Any, TypeVar, Callable
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from cli.enums import TaskStatusEnum, TaskPriorityEnum


class BaseEntity(BaseModel):
    """Base model for all entities with common fields and methods."""
    
    id: UUID = Field(default_factory=uuid4)
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
    parent_id: Optional[UUID] = None
    subtask_ids: Set[UUID] = Field(default_factory=set)
    
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
    
    def add_subtask(self, subtask_id: UUID) -> None:
        """
        Add a subtask to this task.
        
        Args:
            subtask_id: ID of the subtask
        """
        self.subtask_ids.add(subtask_id)
        self.updated_at = datetime.now()
    
    def remove_subtask(self, subtask_id: UUID) -> bool:
        """
        Remove a subtask from this task.
        
        Args:
            subtask_id: ID of the subtask to remove
            
        Returns:
            bool: True if subtask was removed, False if not found
        """
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


class UnifiedTask(BaseTask):
    """Unified task model that combines fields from research and security tasks."""
    
    # Research-specific fields
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    
    # Security-specific fields
    severity: Optional[str] = None
    affected_systems: List[str] = Field(default_factory=list)
    discovered_by: Optional[str] = None


class TaskType(str, Enum):
    """Types of tasks supported by the unified task manager."""
    
    GENERIC = "generic"
    RESEARCH = "research"
    SECURITY = "security"


class BaseStorageInterface:
    """Abstract interface for entity storage implementations."""
    
    def create(self, entity):
        """
        Create a new entity in storage.
        
        Args:
            entity: The entity to create
            
        Returns:
            UUID: The ID of the created entity
        """
        raise NotImplementedError
    
    def get(self, entity_id):
        """
        Retrieve an entity by ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            Optional[Entity]: The entity if found, None otherwise
        """
        raise NotImplementedError
    
    def update(self, entity):
        """
        Update an existing entity.
        
        Args:
            entity: The entity with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        raise NotImplementedError
    
    def delete(self, entity_id):
        """
        Delete an entity by ID.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        raise NotImplementedError
    
    def list(self, filters=None):
        """
        List entities with optional filtering.
        
        Args:
            filters: Optional filters as field-value pairs
            
        Returns:
            List[Entity]: List of entities matching the criteria
        """
        raise NotImplementedError


class InMemoryStorage(BaseStorageInterface):
    """In-memory implementation of entity storage."""
    
    def __init__(self):
        """Initialize the in-memory storage."""
        self._entities = {}
    
    def create(self, entity):
        """
        Create a new entity in storage.
        
        Args:
            entity: The entity to create
            
        Returns:
            UUID: The ID of the created entity
        """
        self._entities[entity.id] = entity
        return entity.id
    
    def get(self, entity_id):
        """
        Retrieve an entity by ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            Optional[Entity]: The entity if found, None otherwise
        """
        return self._entities.get(entity_id)
    
    def update(self, entity):
        """
        Update an existing entity.
        
        Args:
            entity: The entity with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        if entity.id not in self._entities:
            return False
        self._entities[entity.id] = entity
        return True
    
    def delete(self, entity_id):
        """
        Delete an entity by ID.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        if entity_id not in self._entities:
            return False
        del self._entities[entity_id]
        return True
    
    def list(self, filters=None):
        """
        List entities with optional filtering.
        
        Args:
            filters: Optional filters as field-value pairs
            
        Returns:
            List[Entity]: List of entities matching the criteria
        """
        entities = list(self._entities.values())
        
        if not filters:
            return entities
        
        # Apply filters
        filtered_entities = []
        for entity in entities:
            if self._matches_filters(entity, filters):
                filtered_entities.append(entity)
        
        return filtered_entities
    
    def _matches_filters(self, entity, filters):
        """
        Check if an entity matches the given filters.
        
        Args:
            entity: The entity to check
            filters: Filters as field-value pairs
            
        Returns:
            bool: True if the entity matches all filters
        """
        for field, value in filters.items():
            if not hasattr(entity, field):
                return False
                
            field_value = getattr(entity, field)
            
            # Handle list fields like tags
            if isinstance(field_value, list) and not isinstance(value, list):
                if value not in field_value:
                    return False
            # Handle set fields
            elif isinstance(field_value, set) and not isinstance(value, set):
                if value not in field_value:
                    return False
            # Simple equality
            elif field_value != value:
                return False
                
        return True
    
    def get_tasks_by_tag(self, tag):
        """
        Get all tasks with a specific tag.
        
        Args:
            tag: The tag to search for
            
        Returns:
            List[Task]: List of tasks with the tag
        """
        return [
            task for task in self._entities.values()
            if hasattr(task, 'tags') and tag in task.tags
        ]
    
    def get_tasks_by_status(self, status):
        """
        Get all tasks with a specific status.
        
        Args:
            status: The status to search for
            
        Returns:
            List[Task]: List of tasks with the status
        """
        return [
            task for task in self._entities.values()
            if hasattr(task, 'status') and task.status == status
        ]
    
    def get_subtasks(self, parent_id):
        """
        Get all subtasks of a parent task.
        
        Args:
            parent_id: The ID of the parent task
            
        Returns:
            List[Task]: List of subtasks
        """
        return [
            task for task in self._entities.values()
            if hasattr(task, 'parent_id') and task.parent_id == parent_id
        ]


class UnifiedTaskManager:
    """
    Unified task manager that provides operations for both
    researcher and security analyst personas.
    """
    
    def __init__(self, storage=None):
        """
        Initialize the task manager with storage.
        
        Args:
            storage: Optional storage implementation, defaults to InMemoryStorage
        """
        self._storage = storage or InMemoryStorage()
    
    def create_task(
        self,
        title: str,
        description: str,
        task_type: str = TaskType.GENERIC,
        status: str = TaskStatusEnum.PLANNED,
        priority: str = TaskPriorityEnum.MEDIUM,
        due_date: Optional[datetime] = None,
        parent_id: Optional[UUID] = None,
        tags: Optional[Set[str]] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
        # Research-specific fields
        estimated_hours: Optional[float] = None,
        actual_hours: Optional[float] = None,
        # Security-specific fields
        severity: Optional[str] = None,
        affected_systems: Optional[List[str]] = None,
        discovered_by: Optional[str] = None,
    ) -> UUID:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            task_type: Type of task (generic, research, security)
            status: Task status
            priority: Task priority
            due_date: Task due date
            parent_id: Parent task ID if this is a subtask
            tags: Task tags
            custom_metadata: Custom metadata key-value pairs
            estimated_hours: Research-specific - Estimated hours to complete
            actual_hours: Research-specific - Actual hours spent
            severity: Security-specific - Severity level of finding
            affected_systems: Security-specific - List of affected systems
            discovered_by: Security-specific - Person who discovered the issue
            
        Returns:
            UUID: The ID of the created task
            
        Raises:
            ValueError: If parent task doesn't exist
        """
        # Validate parent task if provided
        if parent_id:
            parent_task = self._storage.get(parent_id)
            if not parent_task:
                raise ValueError(f"Parent task with ID {parent_id} does not exist")
        
        # Create task
        task = UnifiedTask(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            parent_id=parent_id,
            tags=tags or set(),
            custom_metadata=custom_metadata or {},
            estimated_hours=estimated_hours,
            actual_hours=actual_hours,
            severity=severity,
            affected_systems=affected_systems or [],
            discovered_by=discovered_by,
        )
        
        # Add task type to metadata
        task.update_custom_metadata("task_type", task_type)
        
        # Save task
        task_id = self._storage.create(task)
        
        # Update parent task if needed
        if parent_id:
            parent_task = self._storage.get(parent_id)
            if parent_task:
                parent_task.add_subtask(task_id)
                self._storage.update(parent_task)
        
        return task_id
    
    def get_task(self, task_id: UUID) -> Optional[UnifiedTask]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Optional[UnifiedTask]: The task if found, None otherwise
        """
        task = self._storage.get(task_id)
        return task
    
    def update_task(
        self,
        task_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[datetime] = None,
        estimated_hours: Optional[float] = None,
        actual_hours: Optional[float] = None,
        severity: Optional[str] = None,
        affected_systems: Optional[List[str]] = None,
        discovered_by: Optional[str] = None,
    ) -> bool:
        """
        Update an existing task.
        
        Args:
            task_id: ID of the task to update
            title: New task title
            description: New task description
            status: New task status
            priority: New task priority
            due_date: New due date
            estimated_hours: New estimated hours
            actual_hours: New actual hours
            severity: New severity level
            affected_systems: New list of affected systems
            discovered_by: New discoverer name
            
        Returns:
            bool: True if update successful, False otherwise
            
        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status
        if priority is not None:
            update_data["priority"] = priority
        if due_date is not None:
            update_data["due_date"] = due_date
        if estimated_hours is not None:
            update_data["estimated_hours"] = estimated_hours
        if actual_hours is not None:
            update_data["actual_hours"] = actual_hours
        if severity is not None:
            update_data["severity"] = severity
        if affected_systems is not None:
            update_data["affected_systems"] = affected_systems
        if discovered_by is not None:
            update_data["discovered_by"] = discovered_by
        
        task.update(**update_data)
        return self._storage.update(task)
    
    def delete_task(self, task_id: UUID) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        return self._storage.delete(task_id)
    
    def list_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[UnifiedTask]:
        """
        List tasks with optional filtering.
        
        Args:
            filters: Optional filters as field-value pairs
            
        Returns:
            List[UnifiedTask]: List of tasks matching the criteria
        """
        return self._storage.list(filters)
    
    def get_tasks_by_type(self, task_type: str) -> List[UnifiedTask]:
        """
        Get tasks by type.
        
        Args:
            task_type: The task type to filter by
            
        Returns:
            List[UnifiedTask]: List of tasks with the specified type
        """
        tasks = self._storage.list()
        return [
            task for task in tasks
            if task.custom_metadata.get("task_type") == task_type
        ]
    
    def get_tasks_by_status(self, status: str) -> List[UnifiedTask]:
        """
        Get tasks by status.
        
        Args:
            status: The status to filter by
            
        Returns:
            List[UnifiedTask]: List of tasks with the specified status
        """
        return self._storage.get_tasks_by_status(status)
    
    def get_tasks_by_tag(self, tag: str) -> List[UnifiedTask]:
        """
        Get tasks by tag.
        
        Args:
            tag: The tag to filter by
            
        Returns:
            List[UnifiedTask]: List of tasks with the specified tag
        """
        return self._storage.get_tasks_by_tag(tag)
    
    def add_task_note(self, task_id: UUID, note: str) -> bool:
        """
        Add a note to a task.
        
        Args:
            task_id: ID of the task
            note: Note content
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        task.add_note(note)
        return self._storage.update(task)
    
    def add_task_tag(self, task_id: UUID, tag: str) -> bool:
        """
        Add a tag to a task.
        
        Args:
            task_id: ID of the task
            tag: Tag to add
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        task.add_tag(tag)
        return self._storage.update(task)
    
    def remove_task_tag(self, task_id: UUID, tag: str) -> bool:
        """
        Remove a tag from a task.
        
        Args:
            task_id: ID of the task
            tag: Tag to remove
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        result = task.remove_tag(tag)
        if result:
            self._storage.update(task)
        return result
"""Base service layer for the unified task manager library.

This module provides shared service layer abstractions that can be used
or extended by persona-specific implementations, ensuring consistent
business logic and reducing code duplication.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set, Union, Any, TypeVar, Generic, Callable
from uuid import UUID

from common.core.models import BaseEntity, BaseTask
from common.core.storage import BaseStorageInterface, BaseTaskStorageInterface


# Generic type for entities (must be a subclass of BaseEntity)
T = TypeVar('T', bound=BaseEntity)


class BaseService(Generic[T]):
    """Base service for entity management."""
    
    def __init__(self, storage: BaseStorageInterface[T]):
        """
        Initialize the service with a storage implementation.
        
        Args:
            storage: Storage implementation for entities
        """
        self._storage = storage
        
        # Optional validator callbacks
        self._validators: Dict[str, Callable[[Any], bool]] = {}
    
    def register_validator(self, field_name: str, validator_func: Callable[[Any], bool]) -> None:
        """
        Register a validator function for a specific field type.
        
        Args:
            field_name: The name of the field to validate
            validator_func: A function that takes a field value and returns True if valid
        """
        self._validators[field_name] = validator_func
    
    def validate_field(self, field_name: str, value: Any) -> bool:
        """
        Validate a field value using the registered validator.
        
        Args:
            field_name: The name of the field to validate
            value: The value to validate
            
        Returns:
            bool: True if field is valid or no validator exists, False otherwise
        """
        if field_name in self._validators:
            return self._validators[field_name](value)
        return True
    
    def create(self, entity: T) -> str:
        """
        Create a new entity.
        
        Args:
            entity: The entity to create
            
        Returns:
            str: The ID of the created entity
        """
        return self._storage.create(entity)
    
    def get(self, entity_id: Union[str, UUID]) -> Optional[T]:
        """
        Retrieve an entity by ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            Optional[T]: The entity if found, None otherwise
        """
        return self._storage.get(entity_id)
    
    def update(self, entity: T) -> bool:
        """
        Update an existing entity.
        
        Args:
            entity: The entity with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        return self._storage.update(entity)
    
    def delete(self, entity_id: Union[str, UUID]) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        return self._storage.delete(entity_id)
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        List entities with optional filtering.
        
        Args:
            filters: Optional filters as field-value pairs
            
        Returns:
            List[T]: List of entities matching the criteria
        """
        return self._storage.list(filters)


class BaseTaskService(BaseService[BaseTask]):
    """Base service for task management."""
    
    def __init__(self, storage: BaseTaskStorageInterface):
        """
        Initialize the service with a storage implementation.
        
        Args:
            storage: Storage implementation for tasks
        """
        super().__init__(storage)
        self._storage = storage  # Typed as BaseTaskStorageInterface for IDE support
    
    def create_task(
        self,
        title: str,
        description: str,
        status: str = "planned",
        priority: str = "medium",
        due_date: Optional[datetime] = None,
        parent_id: Optional[Union[str, UUID]] = None,
        tags: Optional[Set[str]] = None,
        custom_metadata: Optional[Dict[str, Union[str, int, float, bool, list, dict]]] = None,
    ) -> str:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            status: Task status
            priority: Task priority
            due_date: Task due date
            parent_id: Parent task ID if this is a subtask
            tags: Task tags
            custom_metadata: Custom metadata key-value pairs
            
        Returns:
            UUID: The ID of the created task
            
        Raises:
            ValueError: If parent task doesn't exist
        """
        # Validate parent task if provided
        if parent_id:
            # Convert UUID to string if needed
            parent_id_str = str(parent_id) if isinstance(parent_id, UUID) else parent_id
            parent_task = self._storage.get(parent_id_str)
            if not parent_task:
                raise ValueError(f"Parent task with ID {parent_id} does not exist")
        
        # Create task (implementation would be in concrete subclasses)
        task = self._create_task_instance(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            parent_id=parent_id,
            tags=tags or set(),
            custom_metadata=custom_metadata or {},
        )
        
        # Save task
        task_id = self._storage.create(task)
        
        # Update parent task if needed
        if parent_id:
            # Convert UUID to string if needed
            parent_id_str = str(parent_id) if isinstance(parent_id, UUID) else parent_id
            parent_task = self._storage.get(parent_id_str)
            if parent_task:
                parent_task.add_subtask(task_id)
                self._storage.update(parent_task)
        
        return task_id
    
    def _create_task_instance(self, **kwargs) -> BaseTask:
        """
        Create a task instance with the given parameters.
        
        This method should be overridden by concrete subclasses.
        
        Args:
            **kwargs: Task parameters
            
        Returns:
            BaseTask: A new task instance
        """
        # Default implementation creates a BaseTask - subclasses should override
        return BaseTask(**kwargs)
    
    def update_task(
        self,
        task_id: Union[str, UUID],
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[datetime] = None,
    ) -> bool:
        """
        Update an existing task.
        
        Args:
            task_id: The ID of the task to update
            title: New task title
            description: New task description
            status: New task status
            priority: New task priority
            due_date: New due date
            
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
        
        task.update(**update_data)
        return self._storage.update(task)
    
    def get_subtasks(self, parent_id: Union[str, UUID]) -> List[BaseTask]:
        """
        Get all subtasks of a parent task.
        
        Args:
            parent_id: The ID of the parent task
            
        Returns:
            List[BaseTask]: List of subtasks
        """
        return self._storage.get_subtasks(parent_id)
    
    def get_tasks_by_tag(self, tag: str) -> List[BaseTask]:
        """
        Get all tasks with a specific tag.
        
        Args:
            tag: The tag to search for
            
        Returns:
            List[BaseTask]: List of tasks with the tag
        """
        return self._storage.get_tasks_by_tag(tag)
    
    def get_tasks_by_status(self, status: str) -> List[BaseTask]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: The status to search for
            
        Returns:
            List[BaseTask]: List of tasks with the status
        """
        return self._storage.get_tasks_by_status(status)
    
    def add_task_note(self, task_id: Union[str, UUID], note: str) -> bool:
        """
        Add a note to a task.
        
        Args:
            task_id: The ID of the task
            note: The note to add
            
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
    
    def add_task_tag(self, task_id: Union[str, UUID], tag: str) -> bool:
        """
        Add a tag to a task.
        
        Args:
            task_id: The ID of the task
            tag: The tag to add
            
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
    
    def remove_task_tag(self, task_id: Union[str, UUID], tag: str) -> bool:
        """
        Remove a tag from a task.
        
        Args:
            task_id: The ID of the task
            tag: The tag to remove
            
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
    
    def update_task_custom_metadata(
        self, task_id: Union[str, UUID], key: str, value: Union[str, int, float, bool, list, dict]
    ) -> bool:
        """
        Update a custom metadata field on a task.
        
        Args:
            task_id: The ID of the task
            key: The metadata key
            value: The metadata value
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If task doesn't exist
        """
        task = self._storage.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        
        task.update_custom_metadata(key, value)
        return self._storage.update(task)
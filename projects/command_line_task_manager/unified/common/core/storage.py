"""Base storage interfaces and implementations for the unified task manager library.

This module provides shared storage interfaces and basic implementations
that can be used or extended by persona-specific implementations, ensuring
consistent data access patterns and reducing code duplication.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Any, TypeVar, Generic, Callable, Union
from uuid import UUID

from pydantic import BaseModel

from common.core.models import BaseEntity, BaseTask


# Generic type for entities (must be a subclass of BaseEntity)
T = TypeVar('T', bound=BaseEntity)


class BaseStorageInterface(Generic[T], ABC):
    """Abstract interface for entity storage implementations."""
    
    @abstractmethod
    def create(self, entity: T) -> str:
        """
        Create a new entity in storage.
        
        Args:
            entity: The entity to create
            
        Returns:
            str: The ID of the created entity
        """
        pass
    
    @abstractmethod
    def get(self, entity_id: Union[str, UUID]) -> Optional[T]:
        """
        Retrieve an entity by ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            Optional[T]: The entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def update(self, entity: T) -> bool:
        """
        Update an existing entity.
        
        Args:
            entity: The entity with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, entity_id: Union[str, UUID]) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        List entities with optional filtering.
        
        Args:
            filters: Optional filters as field-value pairs
            
        Returns:
            List[T]: List of entities matching the criteria
        """
        pass


class InMemoryStorage(BaseStorageInterface[T]):
    """In-memory implementation of entity storage."""
    
    def __init__(self):
        """Initialize the in-memory storage."""
        self._entities: Dict[str, T] = {}
    
    def create(self, entity: T) -> str:
        """
        Create a new entity in storage.
        
        Args:
            entity: The entity to create
            
        Returns:
            str: The ID of the created entity
        """
        # Ensure ID is a string
        entity_id = str(entity.id)
        self._entities[entity_id] = entity
        return entity_id
    
    def get(self, entity_id: Union[str, UUID]) -> Optional[T]:
        """
        Retrieve an entity by ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            Optional[T]: The entity if found, None otherwise
        """
        # Convert UUID to string if needed
        if isinstance(entity_id, UUID):
            entity_id = str(entity_id)
            
        return self._entities.get(entity_id)
    
    def update(self, entity: T) -> bool:
        """
        Update an existing entity.
        
        Args:
            entity: The entity with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        entity_id = str(entity.id)
        if entity_id not in self._entities:
            return False
        self._entities[entity_id] = entity
        return True
    
    def delete(self, entity_id: Union[str, UUID]) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        # Convert UUID to string if needed
        if isinstance(entity_id, UUID):
            entity_id = str(entity_id)
            
        if entity_id not in self._entities:
            return False
        del self._entities[entity_id]
        return True
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        List entities with optional filtering.
        
        Args:
            filters: Optional filters as field-value pairs
            
        Returns:
            List[T]: List of entities matching the criteria
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
    
    def _matches_filters(self, entity: T, filters: Dict[str, Any]) -> bool:
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
            # Handle date ranges (to be implemented in specific implementations)
            # Simple equality
            elif field_value != value:
                return False
                
        return True


class BaseTaskStorageInterface(BaseStorageInterface[BaseTask], ABC):
    """Abstract interface for task storage implementations."""
    
    @abstractmethod
    def get_subtasks(self, parent_id: Union[str, UUID]) -> List[BaseTask]:
        """
        Get all subtasks of a parent task.
        
        Args:
            parent_id: The ID of the parent task
            
        Returns:
            List[BaseTask]: List of subtasks
        """
        pass
    
    @abstractmethod
    def get_tasks_by_tag(self, tag: str) -> List[BaseTask]:
        """
        Get all tasks with a specific tag.
        
        Args:
            tag: The tag to search for
            
        Returns:
            List[BaseTask]: List of tasks with the tag
        """
        pass
    
    @abstractmethod
    def get_tasks_by_status(self, status: str) -> List[BaseTask]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: The status to search for
            
        Returns:
            List[BaseTask]: List of tasks with the status
        """
        pass


class InMemoryTaskStorage(InMemoryStorage[BaseTask], BaseTaskStorageInterface):
    """In-memory implementation of task storage."""
    
    def get_subtasks(self, parent_id: Union[str, UUID]) -> List[BaseTask]:
        """
        Get all subtasks of a parent task.
        
        Args:
            parent_id: The ID of the parent task
            
        Returns:
            List[BaseTask]: List of subtasks
        """
        # Convert UUID to string if needed
        if isinstance(parent_id, UUID):
            parent_id = str(parent_id)
            
        return [
            task for task in self._entities.values()
            if task.parent_id == parent_id
        ]
    
    def get_tasks_by_tag(self, tag: str) -> List[BaseTask]:
        """
        Get all tasks with a specific tag.
        
        Args:
            tag: The tag to search for
            
        Returns:
            List[BaseTask]: List of tasks with the tag
        """
        return [
            task for task in self._entities.values()
            if tag in task.tags
        ]
    
    def get_tasks_by_status(self, status: str) -> List[BaseTask]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: The status to search for
            
        Returns:
            List[BaseTask]: List of tasks with the status
        """
        return [
            task for task in self._entities.values()
            if task.status == status
        ]
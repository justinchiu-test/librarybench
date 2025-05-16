"""Base storage interfaces and implementations for the unified task manager library.

This module provides shared storage interfaces and basic implementations
that can be used or extended by persona-specific implementations, ensuring
consistent data access patterns and reducing code duplication.
"""

import os
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Any, TypeVar, Generic, Callable, Union, Type
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


class FilePersistentStorage(BaseStorageInterface[T]):
    """
    File-based persistent storage implementation using JSON files.
    
    This class provides a storage implementation that persists entities
    to the filesystem as JSON files, with optional encryption support.
    """
    
    def __init__(
        self, 
        storage_dir: str, 
        entity_type: Type[T],
        crypto_manager = None,
        use_encryption: bool = False
    ):
        """
        Initialize the file storage.
        
        Args:
            storage_dir: Directory to store entity files
            entity_type: The entity type class (used for deserialization)
            crypto_manager: Optional crypto manager for encryption (required if use_encryption is True)
            use_encryption: Whether to encrypt stored files
        """
        self.storage_dir = storage_dir
        self.entity_type = entity_type
        self.crypto_manager = crypto_manager
        self.use_encryption = use_encryption
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
    
    def create(self, entity: T) -> str:
        """
        Create a new entity.
        
        Args:
            entity: The entity to create
            
        Returns:
            str: The ID of the created entity
        """
        entity_id = str(entity.id)
        self._save_entity(entity)
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
            
        file_path = self._get_file_path(entity_id)
        
        if not os.path.exists(file_path):
            return None
            
        try:
            return self._load_entity(entity_id)
        except Exception as e:
            print(f"Error loading entity {entity_id}: {str(e)}")
            return None
    
    def update(self, entity: T) -> bool:
        """
        Update an existing entity.
        
        Args:
            entity: The entity with updated fields
            
        Returns:
            bool: True if update successful, False otherwise
        """
        entity_id = str(entity.id)
        file_path = self._get_file_path(entity_id)
        
        if not os.path.exists(file_path):
            return False
            
        try:
            self._save_entity(entity)
            return True
        except Exception as e:
            print(f"Error updating entity {entity_id}: {str(e)}")
            return False
    
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
            
        file_path = self._get_file_path(entity_id)
        digest_path = self._get_digest_path(entity_id)
        
        if not os.path.exists(file_path):
            return False
            
        try:
            os.remove(file_path)
            if os.path.exists(digest_path):
                os.remove(digest_path)
            return True
        except Exception as e:
            print(f"Error deleting entity {entity_id}: {str(e)}")
            return False
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        List entities with optional filtering.
        
        Args:
            filters: Optional filters as field-value pairs
            
        Returns:
            List[T]: List of entities matching the criteria
        """
        entities = []
        
        # Get all entity IDs from filenames
        for filename in os.listdir(self.storage_dir):
            if self.use_encryption and not filename.endswith(".json.enc"):
                continue
            elif not self.use_encryption and not filename.endswith(".json"):
                continue
                
            entity_id = filename.replace(".json.enc" if self.use_encryption else ".json", "")
            
            try:
                entity = self.get(entity_id)
                if entity and (not filters or self._matches_filters(entity, filters)):
                    entities.append(entity)
            except Exception:
                # Skip invalid files
                continue
                
        return entities
    
    def _get_file_path(self, entity_id: str) -> str:
        """
        Get the file path for an entity.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            str: The file path
        """
        if self.use_encryption:
            return os.path.join(self.storage_dir, f"{entity_id}.json.enc")
        else:
            return os.path.join(self.storage_dir, f"{entity_id}.json")
    
    def _get_digest_path(self, entity_id: str) -> str:
        """
        Get the digest file path for an encrypted entity.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            str: The digest file path
        """
        return os.path.join(self.storage_dir, f"{entity_id}.hmac")
    
    def _save_entity(self, entity: T) -> None:
        """
        Save an entity to storage.
        
        Args:
            entity: The entity to save
        """
        entity_id = str(entity.id)
        file_path = self._get_file_path(entity_id)
        
        # Convert to JSON
        entity_json = entity.model_dump_json().encode()
        
        if self.use_encryption:
            if not self.crypto_manager:
                raise ValueError("Crypto manager is required for encryption")
                
            # Encrypt
            encrypted_data, digest = self.crypto_manager.encrypt(entity_json)
            
            # Save encrypted data
            with open(file_path, "wb") as f:
                f.write(encrypted_data)
                
            # Save HMAC digest separately for integrity verification
            digest_path = self._get_digest_path(entity_id)
            with open(digest_path, "wb") as f:
                f.write(digest)
        else:
            # Save unencrypted
            with open(file_path, "w") as f:
                f.write(entity_json.decode())
    
    def _load_entity(self, entity_id: str) -> T:
        """
        Load an entity from storage.
        
        Args:
            entity_id: The ID of the entity to load
            
        Returns:
            T: The loaded entity
            
        Raises:
            FileNotFoundError: If the entity file doesn't exist
            ValueError: If decryption fails
        """
        file_path = self._get_file_path(entity_id)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Entity not found: {entity_id}")
        
        if self.use_encryption:
            if not self.crypto_manager:
                raise ValueError("Crypto manager is required for decryption")
                
            # Load and decrypt
            with open(file_path, "rb") as f:
                encrypted_data = f.read()
            
            # Load and decrypt the HMAC digest
            digest_path = self._get_digest_path(entity_id)
            with open(digest_path, "rb") as f:
                digest = f.read()
            
            decrypted_data = self.crypto_manager.decrypt(encrypted_data, digest)
            entity_dict = json.loads(decrypted_data.decode())
        else:
            # Load unencrypted
            with open(file_path, "r") as f:
                entity_dict = json.loads(f.read())
        
        # Create the entity object
        return self.entity_type(**entity_dict)
    
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
            # Handle date ranges
            elif field.endswith("_date") and isinstance(value, dict):
                if "from" in value and field_value < value["from"]:
                    return False
                if "to" in value and field_value > value["to"]:
                    return False
            # Simple equality
            elif field_value != value:
                return False
                
        return True


class FileTaskStorage(FilePersistentStorage[BaseTask], BaseTaskStorageInterface):
    """File-based implementation of task storage."""
    
    def __init__(
        self, 
        storage_dir: str, 
        entity_type: Type[BaseTask] = BaseTask,
        crypto_manager = None,
        use_encryption: bool = False
    ):
        """
        Initialize the file task storage.
        
        Args:
            storage_dir: Directory to store task files
            entity_type: The task type class (default is BaseTask)
            crypto_manager: Optional crypto manager for encryption
            use_encryption: Whether to encrypt stored files
        """
        super().__init__(storage_dir, entity_type, crypto_manager, use_encryption)
    
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
            task for task in self.list()
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
            task for task in self.list()
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
            task for task in self.list()
            if task.status == status
        ]
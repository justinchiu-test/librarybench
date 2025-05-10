"""
Base storage functionality for the Academic Knowledge Vault system.

This module defines the abstract interfaces and base implementations for storage.
"""

import json
import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union, Generic

from pydantic import BaseModel

from academic_knowledge_vault.models.base import BaseKnowledgeItem, StorageInfo


T = TypeVar('T', bound=BaseKnowledgeItem)


class StorageError(Exception):
    """Base exception for storage-related errors."""
    pass


class ItemNotFoundError(StorageError):
    """Exception raised when an item is not found in storage."""
    pass


class StoragePermissionError(StorageError):
    """Exception raised when storage operations fail due to permissions."""
    pass


class StorageOperationError(StorageError):
    """Exception raised when a storage operation fails."""
    pass


class StorageCorruptionError(StorageError):
    """Exception raised when stored data is corrupted."""
    pass


class StorageInterface(Generic[T], ABC):
    """Abstract interface for knowledge item storage."""
    
    @abstractmethod
    def save(self, item: T) -> str:
        """
        Save an item to storage.
        
        Args:
            item: The knowledge item to save
            
        Returns:
            The ID of the saved item
            
        Raises:
            StoragePermissionError: If the item cannot be saved due to permissions
            StorageOperationError: If the save operation fails
        """
        pass
    
    @abstractmethod
    def get(self, item_id: str) -> T:
        """
        Retrieve an item from storage by ID.
        
        Args:
            item_id: The ID of the item to retrieve
            
        Returns:
            The retrieved item
            
        Raises:
            ItemNotFoundError: If the item is not found
            StorageCorruptionError: If the stored data is corrupted
            StorageOperationError: If the retrieval operation fails
        """
        pass
    
    @abstractmethod
    def delete(self, item_id: str) -> bool:
        """
        Delete an item from storage.
        
        Args:
            item_id: The ID of the item to delete
            
        Returns:
            True if the item was deleted, False if it didn't exist
            
        Raises:
            StoragePermissionError: If the item cannot be deleted due to permissions
            StorageOperationError: If the delete operation fails
        """
        pass
    
    @abstractmethod
    def list_ids(self) -> List[str]:
        """
        List all item IDs in storage.
        
        Returns:
            A list of item IDs
            
        Raises:
            StorageOperationError: If the list operation fails
        """
        pass
    
    @abstractmethod
    def exists(self, item_id: str) -> bool:
        """
        Check if an item exists in storage.
        
        Args:
            item_id: The ID of the item to check
            
        Returns:
            True if the item exists, False otherwise
        """
        pass
    
    @abstractmethod
    def search(self, query: Dict[str, Any]) -> List[str]:
        """
        Search for items matching the query.
        
        Args:
            query: A dict of field names and values to match
            
        Returns:
            A list of item IDs matching the query
        """
        pass


class JsonFileStorage(StorageInterface[T]):
    """Store knowledge items as JSON files in a directory."""
    
    def __init__(self, 
                 base_dir: Union[str, Path], 
                 model_class: Type[T],
                 create_dir: bool = True):
        """
        Initialize a JSON file storage system.
        
        Args:
            base_dir: Base directory for storage
            model_class: The Pydantic model class to store
            create_dir: Whether to create the directory if it doesn't exist
            
        Raises:
            StoragePermissionError: If the directory cannot be created or accessed
        """
        self.base_dir = Path(base_dir)
        self.model_class = model_class
        
        if create_dir:
            try:
                self.base_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise StoragePermissionError(f"Cannot create directory {self.base_dir}: {e}")
            except OSError as e:
                raise StorageOperationError(f"Error creating directory {self.base_dir}: {e}")
        
        if not self.base_dir.exists() or not self.base_dir.is_dir():
            raise StorageOperationError(f"Storage path {self.base_dir} is not a valid directory")
    
    def _get_file_path(self, item_id: str) -> Path:
        """Get the file path for an item ID."""
        return self.base_dir / f"{item_id}.json"
    
    def save(self, item: T) -> str:
        """
        Save an item to a JSON file.
        
        Args:
            item: The knowledge item to save
            
        Returns:
            The ID of the saved item
            
        Raises:
            StoragePermissionError: If the file cannot be written
            StorageOperationError: If the save operation fails
        """
        try:
            file_path = self._get_file_path(item.id)
            
            # Update the timestamp before saving
            item.updated_at = datetime.now()
            
            # Add storage info to the item if it has that attribute
            if hasattr(item, 'storage'):
                item.storage = StorageInfo(
                    path=file_path,
                    format="json",
                    last_sync=datetime.now()
                )
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(item.model_dump_json(indent=2))
            
            return item.id
            
        except PermissionError as e:
            raise StoragePermissionError(f"Cannot write to {file_path}: {e}")
        except Exception as e:
            raise StorageOperationError(f"Error saving item {item.id}: {e}")
    
    def get(self, item_id: str) -> T:
        """
        Retrieve an item from a JSON file.
        
        Args:
            item_id: The ID of the item to retrieve
            
        Returns:
            The retrieved item
            
        Raises:
            ItemNotFoundError: If the file doesn't exist
            StorageCorruptionError: If the file contains invalid JSON
            StorageOperationError: If the retrieval operation fails
        """
        file_path = self._get_file_path(item_id)
        
        if not file_path.exists():
            raise ItemNotFoundError(f"Item {item_id} not found")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = f.read()
            
            try:
                return self.model_class.model_validate_json(json_data)
            except Exception as e:
                raise StorageCorruptionError(f"Invalid data format for item {item_id}: {e}")
                
        except PermissionError as e:
            raise StoragePermissionError(f"Cannot read {file_path}: {e}")
        except StorageCorruptionError:
            raise
        except Exception as e:
            raise StorageOperationError(f"Error retrieving item {item_id}: {e}")
    
    def delete(self, item_id: str) -> bool:
        """
        Delete an item's JSON file.
        
        Args:
            item_id: The ID of the item to delete
            
        Returns:
            True if the item was deleted, False if it didn't exist
            
        Raises:
            StoragePermissionError: If the file cannot be deleted
            StorageOperationError: If the delete operation fails
        """
        file_path = self._get_file_path(item_id)
        
        if not file_path.exists():
            return False
        
        try:
            file_path.unlink()
            return True
        except PermissionError as e:
            raise StoragePermissionError(f"Cannot delete {file_path}: {e}")
        except Exception as e:
            raise StorageOperationError(f"Error deleting item {item_id}: {e}")
    
    def list_ids(self) -> List[str]:
        """
        List all item IDs in the storage directory.
        
        Returns:
            A list of item IDs
            
        Raises:
            StorageOperationError: If the list operation fails
        """
        try:
            return [
                file_path.stem for file_path in self.base_dir.glob("*.json")
                if file_path.is_file()
            ]
        except Exception as e:
            raise StorageOperationError(f"Error listing items: {e}")
    
    def exists(self, item_id: str) -> bool:
        """
        Check if an item's JSON file exists.
        
        Args:
            item_id: The ID of the item to check
            
        Returns:
            True if the item exists, False otherwise
        """
        return self._get_file_path(item_id).exists()
    
    def search(self, query: Dict[str, Any]) -> List[str]:
        """
        Search for items matching the query.
        
        This is a basic implementation that loads each item and checks manually.
        In a real-world implementation, this would use an index for efficiency.
        
        Args:
            query: A dict of field names and values to match
            
        Returns:
            A list of item IDs matching the query
        """
        if not query:
            return self.list_ids()
            
        result_ids = []
        
        for item_id in self.list_ids():
            try:
                item = self.get(item_id)
                
                # Check if all query conditions match
                matches = True
                for field, value in query.items():
                    if field.startswith("tags__contains"):
                        # Special case for tag checking
                        tag = value
                        if not hasattr(item, "tags") or tag not in item.tags:
                            matches = False
                            break
                    elif not hasattr(item, field) or getattr(item, field) != value:
                        matches = False
                        break
                
                if matches:
                    result_ids.append(item_id)
                    
            except (ItemNotFoundError, StorageCorruptionError):
                # Skip corrupted or missing items
                continue
        
        return result_ids


class StorageManager:
    """Manage multiple storage interfaces for different item types."""
    
    def __init__(self, base_dir: Union[str, Path]):
        """
        Initialize a storage manager.
        
        Args:
            base_dir: Base directory for all storage
            
        Raises:
            StoragePermissionError: If the directory cannot be created or accessed
        """
        self.base_dir = Path(base_dir)
        self.storages: Dict[str, StorageInterface] = {}
        
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise StoragePermissionError(f"Cannot create directory {self.base_dir}: {e}")
        except OSError as e:
            raise StorageOperationError(f"Error creating directory {self.base_dir}: {e}")
    
    def register_storage(self, name: str, storage: StorageInterface) -> None:
        """
        Register a storage interface.
        
        Args:
            name: Name of the storage category
            storage: Storage interface to register
        """
        self.storages[name] = storage
    
    def get_storage(self, name: str) -> StorageInterface:
        """
        Get a registered storage interface.
        
        Args:
            name: Name of the storage category
            
        Returns:
            The requested storage interface
            
        Raises:
            KeyError: If no storage is registered with the given name
        """
        if name not in self.storages:
            raise KeyError(f"No storage registered with name: {name}")
        
        return self.storages[name]
    
    def create_storage_directory(self, subdir: str) -> Path:
        """
        Create a subdirectory for storage.
        
        Args:
            subdir: Name of the subdirectory
            
        Returns:
            Path to the created directory
            
        Raises:
            StoragePermissionError: If the directory cannot be created
            StorageOperationError: If the directory creation fails
        """
        path = self.base_dir / subdir
        
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except PermissionError as e:
            raise StoragePermissionError(f"Cannot create directory {path}: {e}")
        except OSError as e:
            raise StorageOperationError(f"Error creating directory {path}: {e}")
    
    def backup(self, backup_dir: Union[str, Path]) -> Path:
        """
        Create a backup of all storage.
        
        Args:
            backup_dir: Directory to store the backup
            
        Returns:
            Path to the backup directory
            
        Raises:
            StoragePermissionError: If the backup cannot be created
            StorageOperationError: If the backup operation fails
        """
        backup_path = Path(backup_dir) / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copy all files from base_dir to backup_path
            for item in self.base_dir.glob("**/*"):
                if item.is_file():
                    rel_path = item.relative_to(self.base_dir)
                    dest_path = backup_path / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)
            
            return backup_path
            
        except PermissionError as e:
            raise StoragePermissionError(f"Cannot create backup at {backup_path}: {e}")
        except Exception as e:
            raise StorageOperationError(f"Error creating backup: {e}")
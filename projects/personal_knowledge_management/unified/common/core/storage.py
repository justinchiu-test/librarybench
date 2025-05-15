"""Storage system for the unified personal knowledge management system."""

import json
import os
import shutil
import threading
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union
from uuid import UUID

import yaml
from pydantic import BaseModel

from common.core.models import KnowledgeNode

T = TypeVar('T', bound=KnowledgeNode)
MAX_WORKERS = 8  # Maximum number of worker threads for parallel operations


class StorageError(Exception):
    """Exception raised for errors in the storage system."""
    pass


class BaseStorage(ABC):
    """Abstract base class for storage implementations."""
    
    @abstractmethod
    def save(self, item: T) -> None:
        """Save an item to storage.
        
        Args:
            item: The item to save.
        """
        pass
    
    @abstractmethod
    def get(self, model_type: Type[T], item_id: UUID) -> Optional[T]:
        """Retrieve an item by ID.
        
        Args:
            model_type: The type of the item to retrieve.
            item_id: The UUID of the item.
            
        Returns:
            The requested item or None if not found.
        """
        pass
    
    @abstractmethod
    def delete(self, model_type: Type[T], item_id: UUID) -> bool:
        """Delete an item by ID.
        
        Args:
            model_type: The type of the item to delete.
            item_id: The UUID of the item.
            
        Returns:
            True if the item was deleted, False if it wasn't found.
        """
        pass
    
    @abstractmethod
    def list_all(self, model_type: Type[T]) -> List[T]:
        """List all items of a specific type.
        
        Args:
            model_type: The type of items to list.
            
        Returns:
            A list of all items of the specified type.
        """
        pass
    
    @abstractmethod
    def query(self, model_type: Type[T], **filters) -> List[T]:
        """Query items of a specific type with filters.
        
        Args:
            model_type: The type of items to query.
            **filters: Field-value pairs to filter on.
            
        Returns:
            A list of items that match the filters.
        """
        pass
    
    @abstractmethod
    def search_text(self, model_type: Type[T], search_text: str, fields: List[str]) -> List[T]:
        """Search for items containing specific text in certain fields.
        
        Args:
            model_type: The type of items to search.
            search_text: The text to search for.
            fields: The fields to search in.
            
        Returns:
            A list of matching items.
        """
        pass
    
    @abstractmethod
    def save_attachment(self, file_path: Union[str, Path], target_filename: Optional[str] = None) -> Path:
        """Save an attachment file to the storage system.
        
        Args:
            file_path: Path to the file to save.
            target_filename: Optional custom filename to use.
            
        Returns:
            The path where the attachment was saved.
        """
        pass
    
    @abstractmethod
    def get_attachment(self, filename: str) -> Optional[Path]:
        """Get the path to an attachment file.
        
        Args:
            filename: Name of the attachment file.
            
        Returns:
            The path to the attachment or None if not found.
        """
        pass
    
    @abstractmethod
    def backup(self, backup_dir: Union[str, Path]) -> Path:
        """Create a backup of all data.
        
        Args:
            backup_dir: Directory to store the backup.
            
        Returns:
            Path to the created backup directory.
        """
        pass
    
    @abstractmethod
    def restore(self, backup_path: Union[str, Path]) -> None:
        """Restore data from a backup.
        
        Args:
            backup_path: Path to the backup directory.
        """
        pass


class LocalStorage(BaseStorage):
    """Storage system that persists data to the local filesystem."""

    def __init__(self, base_path: Union[str, Path]):
        """Initialize the storage system.
        
        Args:
            base_path: The base directory for storing all data.
        """
        self.base_path = Path(base_path)
        self._ensure_directories()
        self._locks = {}  # Dictionary to store locks for file access
        self._cache = {}  # Simple in-memory cache for frequently accessed items
        self._cache_lock = threading.RLock()  # Lock for cache access

    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            'nodes',  # Generic directory for all node types
            'attachments',
            'backups',
            'indexes',  # For search indexes
        ]

        for directory in directories:
            path = self.base_path / directory
            path.mkdir(parents=True, exist_ok=True)
            
        # Create type-specific subdirectories
        node_path = self.base_path / 'nodes'
        for node_type in ['notes', 'documents', 'citations', 'questions', 
                          'experiments', 'projects', 'people', 'annotations', 'tags', 'other']:
            (node_path / node_type).mkdir(parents=True, exist_ok=True)

    def _get_collection_path(self, model_type: Type[T]) -> Path:
        """Get the path for a specific collection based on model type.
        
        Args:
            model_type: The type of model to determine the collection.
            
        Returns:
            Path to the collection directory.
        """
        # Map model types to directories
        from common.core.models import Annotation, NodeType

        # Default collection path
        nodes_path = self.base_path / 'nodes'
        
        # Get the model name in lowercase
        type_name = model_type.__name__.lower()
        
        # Handle known types with specific directories
        if hasattr(model_type, 'node_type') and isinstance(model_type.node_type, str):
            return nodes_path / model_type.node_type.lower() + 's'
        elif model_type.__name__ == 'Annotation':
            return nodes_path / 'annotations'
        elif type_name.endswith('s'):
            return nodes_path / type_name
        else:
            return nodes_path / f"{type_name}s"

    def _get_lock(self, file_path: Union[str, Path]) -> threading.RLock:
        """Get a lock for a specific file path, creating one if it doesn't exist.
        
        Args:
            file_path: The file path to get a lock for.
            
        Returns:
            A reentrant lock for the file path.
        """
        file_path_str = str(file_path)
        if file_path_str not in self._locks:
            self._locks[file_path_str] = threading.RLock()
        return self._locks[file_path_str]

    def save(self, item: T) -> None:
        """Save an item to storage.
        
        Args:
            item: The item to save.
        """
        collection_path = self._get_collection_path(type(item))
        file_path = collection_path / f"{item.id}.yaml"

        # Update the timestamp
        item.updated_at = datetime.now()

        # Get a lock for this file to prevent concurrent writes
        with self._get_lock(file_path):
            # Convert to dict and handle special object serialization
            data = item.model_dump()

            # Convert UUID objects to strings for serialization
            self._convert_uuids_to_strings(data)

            # Convert Enum objects to strings
            self._convert_enums_to_strings(data)

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            # Update the cache
            self._update_cache(item)

    def _update_cache(self, item: T) -> None:
        """Update the in-memory cache with the latest version of an item.
        
        Args:
            item: The item to cache.
        """
        with self._cache_lock:
            type_name = type(item).__name__
            if type_name not in self._cache:
                self._cache[type_name] = {}
            self._cache[type_name][str(item.id)] = item

    def _get_from_cache(self, model_type: Type[T], item_id: UUID) -> Optional[T]:
        """Try to get an item from the cache.
        
        Args:
            model_type: The type of the item to retrieve.
            item_id: The UUID of the item.
            
        Returns:
            The cached item if found, None otherwise.
        """
        with self._cache_lock:
            type_name = model_type.__name__
            if type_name in self._cache and str(item_id) in self._cache[type_name]:
                return self._cache[type_name][str(item_id)]
        return None

    def _invalidate_cache(self, model_type: Optional[Type[T]] = None, item_id: Optional[UUID] = None) -> None:
        """Invalidate the cache for a specific item or type.
        
        Args:
            model_type: Optional type to invalidate cache for.
            item_id: Optional item ID to invalidate cache for.
        """
        with self._cache_lock:
            if model_type is None:
                self._cache = {}  # Clear the entire cache
            elif item_id is None:
                type_name = model_type.__name__
                if type_name in self._cache:
                    del self._cache[type_name]  # Clear cache for this type
            else:
                type_name = model_type.__name__
                if type_name in self._cache and str(item_id) in self._cache[type_name]:
                    del self._cache[type_name][str(item_id)]  # Clear cache for this item

    def _convert_uuids_to_strings(self, data: Any) -> None:
        """Convert UUID objects to strings in a data structure.
        
        Args:
            data: The data structure to convert, modified in place.
        """
        if isinstance(data, dict):
            for key, value in list(data.items()):
                if isinstance(value, UUID):
                    data[key] = str(value)
                elif isinstance(value, list):
                    self._convert_uuids_to_strings(value)
                elif isinstance(value, dict):
                    self._convert_uuids_to_strings(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, UUID):
                    data[i] = str(item)
                elif isinstance(item, dict):
                    self._convert_uuids_to_strings(item)
                elif isinstance(item, list):
                    self._convert_uuids_to_strings(item)

    def _convert_enums_to_strings(self, data: Any) -> None:
        """Convert Enum objects to strings in a data structure.
        
        Args:
            data: The data structure to convert, modified in place.
        """
        from enum import Enum

        if isinstance(data, dict):
            for key, value in list(data.items()):
                if isinstance(value, Enum):
                    data[key] = value.value
                elif isinstance(value, list):
                    self._convert_enums_to_strings(value)
                elif isinstance(value, dict):
                    self._convert_enums_to_strings(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, Enum):
                    data[i] = item.value
                elif isinstance(item, dict):
                    self._convert_enums_to_strings(item)
                elif isinstance(item, list):
                    self._convert_enums_to_strings(item)

    def _convert_string_to_uuid(self, data: Dict[str, Any]) -> None:
        """Convert string UUIDs back to UUID objects.
        
        Args:
            data: The data structure to convert, modified in place.
        """
        if isinstance(data, dict):
            # Convert 'id' fields to UUID
            if 'id' in data and isinstance(data['id'], str):
                try:
                    data['id'] = UUID(data['id'])
                except ValueError:
                    pass

            # Common UUID fields
            uuid_fields = [
                'source_id', 'target_id', 'node_id', 'author_id', 'parent_id', 
                'resolved_by', 'project_id', 'question_id', 'experiment_id',
                'citation_id', 'document_id', 'creator_id', 'owner_id'
            ]
            
            for field in uuid_fields:
                if field in data and isinstance(data[field], str) and data[field] != 'null':
                    try:
                        data[field] = UUID(data[field])
                    except ValueError:
                        pass

            # Lists of UUIDs
            uuid_list_fields = [
                'references', 'citations', 'notes', 'attachments', 'relations',
                'tags', 'experiments', 'questions', 'documents', 'replies', 
                'related_ids', 'dependencies', 'children', 'parents'
            ]

            for key in uuid_list_fields:
                if key in data and isinstance(data[key], list):
                    for i, item in enumerate(data[key]):
                        if isinstance(item, str):
                            try:
                                data[key][i] = UUID(item)
                            except ValueError:
                                pass

            # Process nested structures
            for key, value in data.items():
                if isinstance(value, dict):
                    self._convert_string_to_uuid(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._convert_string_to_uuid(item)

    def _convert_strings_to_enums(self, data: Dict[str, Any], model_type: Type[T]) -> None:
        """Convert string values back to Enum objects based on the model type.
        
        Args:
            data: The data structure to convert, modified in place.
            model_type: The model type to use for enum conversion.
        """
        # Import enum types
        from common.core.models import Priority, RelationType, Status, NodeType

        # Map field names to enum types
        enum_map = {
            'priority': Priority,
            'relation_type': RelationType,
            'status': Status,
            'node_type': NodeType,
        }

        if isinstance(data, dict):
            for key, value in data.items():
                if key in enum_map and enum_map[key] is not None and isinstance(value, str):
                    try:
                        data[key] = enum_map[key](value)
                    except ValueError:
                        pass
                elif isinstance(value, dict):
                    self._convert_strings_to_enums(value, model_type)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._convert_strings_to_enums(item, model_type)

    def get(self, model_type: Type[T], item_id: UUID) -> Optional[T]:
        """Retrieve an item by ID.
        
        Args:
            model_type: The type of the item to retrieve.
            item_id: The UUID of the item.
            
        Returns:
            The requested item or None if not found.
        """
        # Try to get from cache first
        cached_item = self._get_from_cache(model_type, item_id)
        if cached_item is not None:
            return cached_item

        collection_path = self._get_collection_path(model_type)
        file_path = collection_path / f"{item_id}.yaml"

        if not file_path.exists():
            return None

        try:
            # Use a lock to prevent reading while the file is being written
            with self._get_lock(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                # Convert string UUIDs back to UUID objects
                self._convert_string_to_uuid(data)

                # Convert string values back to Enum objects
                self._convert_strings_to_enums(data, model_type)

                item = model_type(**data)

                # Update the cache
                self._update_cache(item)

                return item
        except (yaml.YAMLError, ValueError) as e:
            raise StorageError(f"Error loading {model_type.__name__} with ID {item_id}: {str(e)}")

    def delete(self, model_type: Type[T], item_id: UUID) -> bool:
        """Delete an item by ID.
        
        Args:
            model_type: The type of the item to delete.
            item_id: The UUID of the item.
            
        Returns:
            True if the item was deleted, False if it wasn't found.
        """
        collection_path = self._get_collection_path(model_type)
        file_path = collection_path / f"{item_id}.yaml"

        if not file_path.exists():
            return False

        # Use a lock to prevent concurrent access
        with self._get_lock(file_path):
            file_path.unlink()

            # Invalidate the cache
            self._invalidate_cache(model_type, item_id)

            return True

    def list_all(self, model_type: Type[T]) -> List[T]:
        """List all items of a specific type.
        
        Args:
            model_type: The type of items to list.
            
        Returns:
            A list of all items of the specified type.
        """
        collection_path = self._get_collection_path(model_type)
        file_paths = list(collection_path.glob('*.yaml'))

        if not file_paths:
            return []

        # Use ThreadPoolExecutor for parallel loading
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Load each file in parallel
            future_to_path = {
                executor.submit(self._load_item_from_file, file_path, model_type): file_path
                for file_path in file_paths
            }

            # Collect results as they complete
            results = []
            for future in future_to_path:
                try:
                    item = future.result()
                    if item is not None:
                        results.append(item)
                except Exception as e:
                    # Log the error but continue processing other items
                    print(f"Error loading item: {e}")

            return results

    def _load_item_from_file(self, file_path: Path, model_type: Type[T]) -> Optional[T]:
        """Load an item from a file.
        
        Args:
            file_path: The path to the file.
            model_type: The type of the item to load.
            
        Returns:
            The loaded item or None if loading failed.
        """
        # Extract the UUID from the filename
        try:
            item_id = UUID(file_path.stem)

            # Check cache first
            cached_item = self._get_from_cache(model_type, item_id)
            if cached_item is not None:
                return cached_item

            # Use a lock to prevent reading while the file is being written
            with self._get_lock(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                # Convert string UUIDs back to UUID objects
                self._convert_string_to_uuid(data)

                # Convert string values back to Enum objects
                self._convert_strings_to_enums(data, model_type)

                item = model_type(**data)

                # Update the cache
                self._update_cache(item)

                return item
        except Exception as e:
            # Print error for debugging but don't raise
            print(f"Error loading {file_path}: {e}")
            return None

    def query(self, model_type: Type[T], **filters) -> List[T]:
        """Query items of a specific type with filters.
        
        Args:
            model_type: The type of items to query.
            **filters: Field-value pairs to filter on.
            
        Returns:
            A list of items that match the filters.
        """
        all_items = self.list_all(model_type)
        result = []

        for item in all_items:
            match = True
            item_dict = item.model_dump()

            for field, value in filters.items():
                if field not in item_dict or item_dict[field] != value:
                    match = False
                    break

            if match:
                result.append(item)

        return result

    def save_attachment(self, file_path: Union[str, Path], target_filename: Optional[str] = None) -> Path:
        """Save an attachment file to the storage system.
        
        Args:
            file_path: Path to the file to save.
            target_filename: Optional custom filename to use.
            
        Returns:
            The path where the attachment was saved.
        """
        source_path = Path(file_path)

        if not source_path.exists():
            raise StorageError(f"Attachment file not found: {file_path}")

        if target_filename is None:
            target_filename = source_path.name

        attachments_dir = self.base_path / 'attachments'
        target_path = attachments_dir / target_filename

        # Use a lock to prevent concurrent writes
        with self._get_lock(target_path):
            # Copy the file
            shutil.copy2(source_path, target_path)

        return target_path

    def get_attachment(self, filename: str) -> Optional[Path]:
        """Get the path to an attachment file.
        
        Args:
            filename: Name of the attachment file.
            
        Returns:
            The path to the attachment or None if not found.
        """
        attachments_dir = self.base_path / 'attachments'
        file_path = attachments_dir / filename

        if file_path.exists():
            return file_path
        return None

    def search_text(self, model_type: Type[T], search_text: str, fields: List[str]) -> List[T]:
        """Search for items containing specific text in certain fields.
        
        Args:
            model_type: The type of items to search.
            search_text: The text to search for.
            fields: The fields to search in.
            
        Returns:
            A list of matching items.
        """
        # Try to use the index if available
        try:
            matching_ids = self.search_index(model_type, search_text, fields)
            if matching_ids:
                # Load the matching items
                return [self.get(model_type, item_id) for item_id in matching_ids if self.get(model_type, item_id) is not None]
        except Exception as e:
            # Fall back to manual search if index search fails
            print(f"Search index error: {e}")
            pass

        # Manual search
        all_items = self.list_all(model_type)
        result = []
        search_text_lower = search_text.lower()

        for item in all_items:
            item_dict = item.model_dump()

            for field in fields:
                if field in item_dict and isinstance(item_dict[field], str):
                    field_value = item_dict[field].lower()
                    if search_text_lower in field_value:
                        if item not in result:
                            result.append(item)
                        break

        return result

    def build_search_index(self, model_type: Type[T], fields: List[str]) -> None:
        """Build a search index for a specific model type and fields.
        
        Args:
            model_type: The type of items to index.
            fields: The fields to index.
        """
        items = self.list_all(model_type)
        if not items:
            return

        # Create a simplified index structure for each field
        indexes = {}
        for field in fields:
            indexes[field] = {}

        # Build the index
        for item in items:
            item_dict = item.model_dump()
            item_id = str(item.id)

            for field in fields:
                if field in item_dict and isinstance(item_dict[field], str):
                    # Tokenize the field content
                    tokens = item_dict[field].lower().split()
                    # Add item ID to the index for each token
                    for token in tokens:
                        if token not in indexes[field]:
                            indexes[field][token] = set()
                        indexes[field][token].add(item_id)

        # Save the index
        index_path = self.base_path / 'indexes' / f"{model_type.__name__.lower()}_index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            # Convert sets to lists for JSON serialization
            for field in indexes:
                for token in indexes[field]:
                    indexes[field][token] = list(indexes[field][token])
            json.dump(indexes, f, indent=2)

    def search_index(self, model_type: Type[T], search_text: str, fields: List[str]) -> List[UUID]:
        """Search the index for items matching the search text.
        
        Args:
            model_type: The type of items to search.
            search_text: The text to search for.
            fields: The fields to search in.
            
        Returns:
            A list of UUIDs of matching items.
        """
        index_path = self.base_path / 'indexes' / f"{model_type.__name__.lower()}_index.json"
        if not index_path.exists():
            # If index doesn't exist, build it
            self.build_search_index(model_type, fields)

            # If it still doesn't exist, fall back to text search
            if not index_path.exists():
                items = self.search_text(model_type, search_text, fields)
                return [item.id for item in items]

        # Load the index
        with open(index_path, 'r', encoding='utf-8') as f:
            indexes = json.load(f)

        # Tokenize the search text
        tokens = search_text.lower().split()

        # Find matching items
        matching_ids = set()
        first_match = True

        for token in tokens:
            token_matches = set()

            for field in fields:
                if field in indexes:
                    for indexed_token, item_ids in indexes[field].items():
                        if token in indexed_token:
                            token_matches.update(item_ids)

            # Intersect with previous matches
            if first_match:
                matching_ids = token_matches
                first_match = False
            else:
                matching_ids &= token_matches

        # Convert matching IDs to UUID objects
        return [UUID(item_id) for item_id in matching_ids]

    def backup(self, backup_dir: Union[str, Path]) -> Path:
        """Create a backup of all data.
        
        Args:
            backup_dir: Directory to store the backup.
            
        Returns:
            Path to the created backup directory.
        """
        backup_path = Path(backup_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir = backup_path / f"knowledge_backup_{timestamp}"

        target_dir.mkdir(parents=True, exist_ok=True)

        # Create the data directory
        (target_dir / 'data').mkdir(parents=True, exist_ok=True)

        # Ensure all directories exist in the backup
        (target_dir / 'data' / 'nodes').mkdir(parents=True, exist_ok=True)
        (target_dir / 'data' / 'attachments').mkdir(parents=True, exist_ok=True)
        (target_dir / 'data' / 'indexes').mkdir(parents=True, exist_ok=True)

        # Create subdirectories for node types
        nodes_dir = target_dir / 'data' / 'nodes'
        for node_type in ['notes', 'documents', 'citations', 'questions', 
                          'experiments', 'projects', 'people', 'annotations', 'tags', 'other']:
            (nodes_dir / node_type).mkdir(parents=True, exist_ok=True)

        # Use a thread pool for parallel copying
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []

            # Copy files selectively to avoid recursively copying previous backups
            for item in sorted(self.base_path.glob('*')):
                # Skip previous backups
                if item.name == 'backups':
                    continue

                if item.is_dir():
                    # Create the directory in the target
                    (target_dir / 'data' / item.name).mkdir(parents=True, exist_ok=True)

                    # Copy all files in the directory
                    for file_path in item.glob('**/*'):
                        if file_path.is_file():
                            # Determine the relative path from the base path
                            rel_path = file_path.relative_to(self.base_path)
                            dest_path = target_dir / 'data' / rel_path
                            
                            # Ensure parent directories exist
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Schedule the copy operation
                            futures.append(executor.submit(shutil.copy2, file_path, dest_path))
                elif item.is_file():
                    # Copy the file
                    dest_path = target_dir / 'data' / item.name
                    futures.append(executor.submit(shutil.copy2, item, dest_path))

            # Wait for all copy operations to complete
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"Error during backup: {e}")

        # Create a metadata file with backup information
        metadata = {
            "backup_time": timestamp,
            "version": "1.0",
            "directories": list(str(path) for path in (target_dir / 'data').glob('*')),
        }

        with open(target_dir / 'backup_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        return target_dir

    def restore(self, backup_path: Union[str, Path]) -> None:
        """Restore data from a backup.
        
        Args:
            backup_path: Path to the backup directory.
        """
        source_path = Path(backup_path) / 'data'

        if not source_path.exists():
            raise StorageError(f"Backup data not found at {source_path}")

        # Clear the cache
        self._invalidate_cache()

        # Clear existing data, but skip the backups directory
        for item in self.base_path.glob('*'):
            if item.name == 'backups':
                continue

            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

        # Make sure all necessary directories exist in the target
        self._ensure_directories()

        # Use a thread pool for parallel copying
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []

            # Copy from backup
            for item in source_path.glob('*'):
                if item.is_dir():
                    # Create the directory in the target
                    target_dir = self.base_path / item.name
                    target_dir.mkdir(parents=True, exist_ok=True)

                    # Copy all files in the directory recursively
                    for file_path in item.glob('**/*'):
                        if file_path.is_file():
                            # Determine the relative path from the source path
                            rel_path = file_path.relative_to(source_path)
                            dest_path = self.base_path / rel_path
                            
                            # Ensure parent directories exist
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Schedule the copy operation
                            futures.append(executor.submit(shutil.copy2, file_path, dest_path))
                elif item.is_file():
                    # Copy the file
                    dest_path = self.base_path / item.name
                    futures.append(executor.submit(shutil.copy2, item, dest_path))

            # Wait for all copy operations to complete
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"Error during restore: {e}")

        # Clear the cache to ensure we load fresh data
        self._invalidate_cache()
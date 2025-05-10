"""
Base storage module for ProductInsight.

This module defines the interfaces and base implementations for data storage,
supporting the requirement for plain text file-based storage.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

import yaml
from pydantic import BaseModel

from product_insight.models import BaseEntity

T = TypeVar("T", bound=BaseEntity)


class StorageError(Exception):
    """Base exception for storage errors."""
    pass


class EntityNotFoundError(StorageError):
    """Exception raised when an entity is not found."""
    pass


class StorageInterface(Generic[T]):
    """Interface for entity storage."""
    
    def save(self, entity: T) -> T:
        """Save an entity to storage."""
        raise NotImplementedError
    
    def get(self, entity_id: UUID) -> T:
        """Retrieve an entity by its ID."""
        raise NotImplementedError
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """List entities, optionally filtered."""
        raise NotImplementedError
    
    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by its ID."""
        raise NotImplementedError
    
    def update(self, entity: T) -> T:
        """Update an existing entity."""
        raise NotImplementedError


class FileStorage(StorageInterface[T]):
    """File-based storage implementation."""
    
    def __init__(
        self, 
        entity_type: Type[T], 
        storage_dir: Union[str, Path],
        format: str = "json"
    ):
        """Initialize the file storage.
        
        Args:
            entity_type: The Pydantic model class for the entities
            storage_dir: Directory path for storing entities
            format: Storage format (json, yaml, or markdown)
        """
        self.entity_type = entity_type
        self.storage_dir = Path(storage_dir)
        self.format = format.lower()
        
        if self.format not in ("json", "yaml", "markdown"):
            raise ValueError(f"Unsupported format: {format}")
        
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _get_file_path(self, entity_id: UUID) -> Path:
        """Get the file path for an entity."""
        if self.format == "json":
            return self.storage_dir / f"{entity_id}.json"
        elif self.format == "yaml":
            return self.storage_dir / f"{entity_id}.yaml"
        else:  # markdown
            return self.storage_dir / f"{entity_id}.md"
    
    def _serialize(self, entity: T) -> str:
        """Serialize an entity to the storage format."""
        entity_dict = entity.model_dump()
        
        if self.format == "json":
            return json.dumps(entity_dict, default=self._json_serializer, indent=2)
        elif self.format == "yaml":
            return yaml.dump(entity_dict, default_flow_style=False)
        else:  # markdown
            md_content = f"# {entity_dict.get('name', '') or entity_dict.get('title', '')}\n\n"
            md_content += f"ID: {entity_dict.get('id')}\n\n"
            
            # Add other fields
            for key, value in entity_dict.items():
                if key in ("id", "name", "title"):
                    continue
                md_content += f"## {key}\n\n"
                md_content += f"{value}\n\n"
            
            return md_content
    
    def _deserialize(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Deserialize content from the storage format."""
        if self.format == "json":
            return json.loads(content)
        elif self.format == "yaml":
            return yaml.safe_load(content)
        else:  # markdown - basic implementation
            # This is a simplified implementation, a real one would be more robust
            entity_dict = {}
            lines = content.splitlines()
            
            # Extract ID from the second line
            for line in lines:
                if line.startswith("ID: "):
                    entity_dict["id"] = line[4:].strip()
                    break
            
            # Extract name or title from the first line
            if lines and lines[0].startswith("# "):
                title = lines[0][2:].strip()
                if hasattr(self.entity_type, "name"):
                    entity_dict["name"] = title
                else:
                    entity_dict["title"] = title
            
            return entity_dict
    
    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for handling UUID and datetime."""
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)
    
    def save(self, entity: T) -> T:
        """Save an entity to a file."""
        entity.update_timestamp()
        file_path = self._get_file_path(entity.id)
        content = self._serialize(entity)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return entity
    
    def get(self, entity_id: UUID) -> T:
        """Retrieve an entity by its ID."""
        file_path = self._get_file_path(entity_id)
        
        if not file_path.exists():
            raise EntityNotFoundError(f"Entity with ID {entity_id} not found")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        entity_dict = self._deserialize(content, file_path)
        return self.entity_type.model_validate(entity_dict)
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """List entities, optionally filtered."""
        entities = []
        extension = f".{self.format}" if self.format != "markdown" else ".md"
        
        for file_path in self.storage_dir.glob(f"*{extension}"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                entity_dict = self._deserialize(content, file_path)
                entity = self.entity_type.model_validate(entity_dict)
                
                # Apply filters if provided
                if filters:
                    include = True
                    for key, value in filters.items():
                        if hasattr(entity, key):
                            attr_value = getattr(entity, key)
                            if attr_value != value:
                                include = False
                                break
                    
                    if not include:
                        continue
                
                entities.append(entity)
            except Exception as e:
                print(f"Error loading entity from {file_path}: {e}")
        
        return entities
    
    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by its ID."""
        file_path = self._get_file_path(entity_id)
        
        if not file_path.exists():
            raise EntityNotFoundError(f"Entity with ID {entity_id} not found")
        
        try:
            file_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting entity {entity_id}: {e}")
            return False
    
    def update(self, entity: T) -> T:
        """Update an existing entity."""
        file_path = self._get_file_path(entity.id)
        
        if not file_path.exists():
            raise EntityNotFoundError(f"Entity with ID {entity.id} not found")
        
        return self.save(entity)
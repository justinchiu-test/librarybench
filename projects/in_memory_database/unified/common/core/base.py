"""
Base classes for the common library.

This module provides abstract base classes that serve as the foundation for both
vectordb and syncdb implementations. These classes define common interfaces and
behaviors for records, collections, and operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, TypeVar, Generic, Iterator
import json
import uuid
import time
from datetime import datetime

T = TypeVar('T', bound='BaseRecord')

class BaseRecord(ABC):
    """
    Abstract base class for all record types.
    
    This class defines the common attributes and behaviors for records in both
    vectordb and syncdb implementations.
    """
    
    def __init__(
        self,
        id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None
    ) -> None:
        """
        Initialize a base record.
        
        Args:
            id: Unique identifier for the record. If None, it will remain None. 
                 Subclasses may choose to generate a default ID.
            metadata: Optional metadata associated with the record.
            created_at: Timestamp when the record was created. If None, current time is used.
            updated_at: Timestamp when the record was last updated. If None, created_at is used.
        """
        self.id = id  # Keep id exactly as provided, allows None
        self.metadata = metadata or {}
        self.created_at = created_at if created_at is not None else time.time()
        self.updated_at = updated_at if updated_at is not None else self.created_at
    
    def update(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the record's metadata and update timestamp.
        
        Args:
            metadata: New metadata to update or add to the record.
        """
        if metadata:
            self.metadata.update(metadata)
        self.updated_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the record to a dictionary representation.
        
        Returns:
            A dictionary containing the record's data.
        """
        return {
            'id': self.id,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseRecord':
        """
        Create a record from a dictionary representation.
        
        Args:
            data: Dictionary containing record data.
        
        Returns:
            A new BaseRecord instance.
        """
        return cls(
            id=data.get('id'),
            metadata=data.get('metadata', {}),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_json(self) -> str:
        """
        Convert the record to a JSON string.
        
        Returns:
            JSON representation of the record.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseRecord':
        """
        Create a record from a JSON string.
        
        Args:
            json_str: JSON string representing the record.
        
        Returns:
            A new BaseRecord instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __eq__(self, other: object) -> bool:
        """
        Check if two records are equal by comparing their IDs.
        
        Args:
            other: The object to compare with.
            
        Returns:
            True if the records have the same ID, False otherwise.
        """
        if not isinstance(other, BaseRecord):
            return False
        return self.id == other.id


class BaseCollection(Generic[T], ABC):
    """
    Abstract base class for collections of records.
    
    This class defines common behaviors for collections of records, such as
    adding, retrieving, updating, and deleting records.
    """
    
    def __init__(self) -> None:
        """
        Initialize a base collection.
        """
        self._records: Dict[str, T] = {}
    
    def add(self, record: T) -> str:
        """
        Add a record to the collection.
        
        Args:
            record: The record to add.
            
        Returns:
            The ID of the added record.
            
        Raises:
            ValueError: If the record's ID is None.
        """
        if record.id is None:
            raise ValueError("Record ID cannot be None when adding to a collection")
        self._records[record.id] = record
        return record.id
    
    def get(self, record_id: str) -> Optional[T]:
        """
        Get a record by ID.
        
        Args:
            record_id: The ID of the record to retrieve.
            
        Returns:
            The record if found, None otherwise.
        """
        return self._records.get(record_id)
    
    def update(self, record_id: str, **kwargs: Any) -> Optional[T]:
        """
        Update a record by ID.
        
        Args:
            record_id: The ID of the record to update.
            **kwargs: The attributes to update.
            
        Returns:
            The updated record if found, None otherwise.
        """
        record = self.get(record_id)
        if record:
            for key, value in kwargs.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            record.updated_at = time.time()
            return record
        return None
    
    def delete(self, record_id: str) -> bool:
        """
        Delete a record by ID.
        
        Args:
            record_id: The ID of the record to delete.
            
        Returns:
            True if the record was deleted, False otherwise.
        """
        if record_id in self._records:
            del self._records[record_id]
            return True
        return False
    
    def list(self) -> List[T]:
        """
        List all records in the collection.
        
        Returns:
            A list of all records.
        """
        return list(self._records.values())
    
    def count(self) -> int:
        """
        Count the number of records in the collection.
        
        Returns:
            The number of records.
        """
        return len(self._records)
    
    def clear(self) -> None:
        """
        Clear all records from the collection.
        """
        self._records.clear()
    
    def __iter__(self) -> Iterator[T]:
        """
        Iterator for the collection.
        
        Returns:
            An iterator over the records in the collection.
        """
        return iter(self._records.values())
    
    def __len__(self) -> int:
        """
        Get the number of records in the collection.
        
        Returns:
            The number of records.
        """
        return self.count()
    
    def __contains__(self, record_id: str) -> bool:
        """
        Check if a record with the given ID exists in the collection.
        
        Args:
            record_id: The ID to check.
            
        Returns:
            True if the record exists, False otherwise.
        """
        return record_id in self._records


class BaseOperation(ABC):
    """
    Abstract base class for operations on records and collections.
    
    This class defines the interface for operations that can be performed on
    records and collections, such as transformations, queries, etc.
    """
    
    def __init__(self, name: str, description: Optional[str] = None) -> None:
        """
        Initialize a base operation.
        
        Args:
            name: The name of the operation.
            description: Optional description of the operation.
        """
        self.name = name
        self.description = description
        self.created_at = time.time()
    
    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the operation.
        
        Args:
            *args: Positional arguments for the operation.
            **kwargs: Keyword arguments for the operation.
            
        Returns:
            The result of the operation.
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the operation to a dictionary representation.
        
        Returns:
            A dictionary containing the operation's data.
        """
        return {
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseOperation':
        """
        Create an operation from a dictionary representation.
        
        Args:
            data: Dictionary containing operation data.
        
        Returns:
            A new BaseOperation instance.
        """
        return cls(
            name=data['name'],
            description=data.get('description')
        )
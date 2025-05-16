"""
Storage classes for the common library.

This module provides storage mechanisms that can be used by both vectordb and
syncdb implementations. It focuses on in-memory storage with efficient indexing
and retrieval capabilities.
"""

from typing import Any, Dict, List, Optional, Set, TypeVar, Generic, Iterator, Callable, Tuple
import time
import json
import uuid
from collections import defaultdict

from .base import BaseRecord, BaseCollection

T = TypeVar('T', bound=BaseRecord)

class Index(Generic[T]):
    """
    An index for efficient querying of records by field values.
    
    This class maintains a mapping of field values to record IDs for
    quick lookups and filtering.
    """
    
    def __init__(self, field_name: str) -> None:
        """
        Initialize an index for a specific field.
        
        Args:
            field_name: The name of the field to index.
        """
        self.field_name = field_name
        self._index: Dict[Any, Set[str]] = defaultdict(set)
    
    def add(self, record: T) -> None:
        """
        Add a record to the index.
        
        Args:
            record: The record to index.
        """
        value = self._get_field_value(record)
        if value is not None:
            self._index[value].add(record.id)
    
    def remove(self, record: T) -> None:
        """
        Remove a record from the index.
        
        Args:
            record: The record to remove.
        """
        value = self._get_field_value(record)
        if value is not None and value in self._index:
            self._index[value].discard(record.id)
            if not self._index[value]:
                del self._index[value]
    
    def update(self, old_record: T, new_record: T) -> None:
        """
        Update a record in the index.
        
        Args:
            old_record: The old version of the record.
            new_record: The new version of the record.
        """
        self.remove(old_record)
        self.add(new_record)
    
    def find(self, value: Any) -> Set[str]:
        """
        Find record IDs with a specific field value.
        
        Args:
            value: The value to search for.
        
        Returns:
            A set of record IDs that match the value.
        """
        return self._index.get(value, set())
    
    def clear(self) -> None:
        """
        Clear all entries from the index.
        """
        self._index.clear()
    
    def _get_field_value(self, record: T) -> Any:
        """
        Get the value of the indexed field from a record.
        
        Args:
            record: The record to extract the field value from.
        
        Returns:
            The value of the field, or None if the field doesn't exist.
        """
        # Check in record attributes first
        if hasattr(record, self.field_name):
            return getattr(record, self.field_name)
        
        # Then check in metadata
        if hasattr(record, 'metadata') and self.field_name in record.metadata:
            return record.metadata[self.field_name]
        
        return None


class InMemoryStorage(BaseCollection[T]):
    """
    In-memory storage for records with indexing capabilities.
    
    This class extends BaseCollection with additional features like indexing,
    filtering, and advanced querying.
    """
    
    def __init__(self) -> None:
        """
        Initialize an in-memory storage.
        """
        super().__init__()
        self._indices: Dict[str, Index[T]] = {}
        self._last_modified: float = time.time()
    
    def add_index(self, field_name: str) -> None:
        """
        Add an index for a specific field.
        
        Args:
            field_name: The name of the field to index.
        """
        if field_name not in self._indices:
            self._indices[field_name] = Index[T](field_name)
            
            # Index existing records
            for record in self._records.values():
                self._indices[field_name].add(record)
    
    def remove_index(self, field_name: str) -> None:
        """
        Remove an index for a specific field.
        
        Args:
            field_name: The name of the field to remove the index for.
        """
        if field_name in self._indices:
            del self._indices[field_name]
    
    def add(self, record: T) -> str:
        """
        Add a record to the storage.
        
        Args:
            record: The record to add.
        
        Returns:
            The ID of the added record.
            
        Raises:
            ValueError: If the record's ID is None.
        """
        if record.id is None:
            raise ValueError("Record ID cannot be None when adding to storage")
            
        record_id = super().add(record)
        
        # Update indices
        for index in self._indices.values():
            index.add(record)
        
        self._last_modified = time.time()
        return record_id
    
    def update(self, record_id: str, **kwargs: Any) -> Optional[T]:
        """
        Update a record by ID.
        
        Args:
            record_id: The ID of the record to update.
            **kwargs: The attributes to update.
        
        Returns:
            The updated record if found, None otherwise.
        """
        old_record = self.get(record_id)
        if old_record:
            # Create a new record with updated values for indexing
            updated_record = self.get(record_id)
            
            for key, value in kwargs.items():
                if hasattr(updated_record, key):
                    setattr(updated_record, key, value)
            
            updated_record.updated_at = time.time()
            
            # Update indices
            for index in self._indices.values():
                index.update(old_record, updated_record)
            
            self._last_modified = time.time()
            return updated_record
        
        return None
    
    def delete(self, record_id: str) -> bool:
        """
        Delete a record by ID.
        
        Args:
            record_id: The ID of the record to delete.
        
        Returns:
            True if the record was deleted, False otherwise.
        """
        record = self.get(record_id)
        if record:
            # Remove from indices first
            for index in self._indices.values():
                index.remove(record)
            
            # Then remove from storage
            super().delete(record_id)
            
            self._last_modified = time.time()
            return True
        
        return False
    
    def query(self, field_name: str, value: Any) -> List[T]:
        """
        Query records by field value.
        
        Args:
            field_name: The name of the field to query.
            value: The value to search for.
        
        Returns:
            A list of records that match the query.
        """
        if field_name in self._indices:
            # Use index for efficient lookup
            record_ids = self._indices[field_name].find(value)
            return [self._records[record_id] for record_id in record_ids if record_id in self._records]
        else:
            # Fallback to linear search
            results = []
            for record in self._records.values():
                field_value = getattr(record, field_name, None)
                if field_value is None and hasattr(record, 'metadata'):
                    field_value = record.metadata.get(field_name)
                
                if field_value == value:
                    results.append(record)
            
            return results
    
    def filter(self, predicate: Callable[[T], bool]) -> List[T]:
        """
        Filter records using a predicate function.
        
        Args:
            predicate: A function that takes a record and returns a boolean.
        
        Returns:
            A list of records for which the predicate returns True.
        """
        return [record for record in self._records.values() if predicate(record)]
    
    def clear(self) -> None:
        """
        Clear all records from the storage and reset indices.
        """
        super().clear()
        for index in self._indices.values():
            index.clear()
        
        self._last_modified = time.time()
    
    def batch_add(self, records: List[T]) -> List[str]:
        """
        Add multiple records in a single batch operation.
        
        Args:
            records: The records to add.
        
        Returns:
            A list of IDs for the added records.
        """
        record_ids = []
        for record in records:
            record_id = self.add(record)
            record_ids.append(record_id)
        
        return record_ids
    
    def batch_update(self, updates: List[Tuple[str, Dict[str, Any]]]) -> List[Optional[T]]:
        """
        Update multiple records in a single batch operation.
        
        Args:
            updates: A list of tuples containing record IDs and update dictionaries.
        
        Returns:
            A list of updated records, with None for records that were not found.
        """
        updated_records = []
        for record_id, update_dict in updates:
            updated_record = self.update(record_id, **update_dict)
            updated_records.append(updated_record)
        
        return updated_records
    
    def batch_delete(self, record_ids: List[str]) -> List[bool]:
        """
        Delete multiple records in a single batch operation.
        
        Args:
            record_ids: The IDs of the records to delete.
        
        Returns:
            A list of booleans indicating whether each record was deleted.
        """
        results = []
        for record_id in record_ids:
            result = self.delete(record_id)
            results.append(result)
        
        return results
    
    def get_last_modified(self) -> float:
        """
        Get the timestamp of the last modification to the storage.
        
        Returns:
            The timestamp of the last modification.
        """
        return self._last_modified
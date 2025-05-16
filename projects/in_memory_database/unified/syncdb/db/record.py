"""
Record classes for the SyncDB database.
"""
from typing import Dict, List, Any, Optional, Tuple
import time
import copy

from common.core.base import BaseRecord
from common.core.serialization import Serializable


class TableRecord(BaseRecord, Serializable):
    """
    Represents a record in a database table that wraps the raw data and
    provides the necessary interface for the common library's storage.
    """
    
    def __init__(
        self,
        data: Dict[str, Any],
        primary_key_tuple: Tuple,
        id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None
    ) -> None:
        """
        Initialize a table record.
        
        Args:
            data: The record data.
            primary_key_tuple: The primary key tuple for this record.
            id: Optional unique identifier. If None, generated from primary_key_tuple.
            metadata: Optional metadata.
            created_at: Timestamp when the record was created.
            updated_at: Timestamp when the record was last updated.
        """
        # Use primary key tuple as ID if not provided
        if id is None:
            id = str(primary_key_tuple)
        
        # Set created_at from the record data if available
        record_created_at = data.get('created_at')
        if created_at is None and record_created_at is not None:
            created_at = record_created_at
            
        # Set updated_at from the record data if available
        record_updated_at = data.get('updated_at')
        if updated_at is None and record_updated_at is not None:
            updated_at = record_updated_at
            
        super().__init__(
            id=id,
            metadata=metadata or {},
            created_at=created_at,
            updated_at=updated_at
        )
        
        # Store the raw data and primary key tuple
        self.data = copy.deepcopy(data)
        self.primary_key_tuple = primary_key_tuple
        
        # Ensure created_at and updated_at are in the data
        if 'created_at' not in self.data:
            self.data['created_at'] = self.created_at
        if 'updated_at' not in self.data:
            self.data['updated_at'] = self.updated_at
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], primary_key_fields: Optional[List[str]] = None) -> 'TableRecord':
        """
        Create a TableRecord from a dictionary representation.
        
        Args:
            data: Dictionary containing record data.
            primary_key_fields: List of field names that make up the primary key.
            
        Returns:
            A new TableRecord instance.
        """
        # If this is coming from BaseRecord.from_dict, it will have different fields
        if 'data' in data and 'primary_key_tuple' in data:
            # This is a serialized TableRecord
            return cls(
                data=data['data'],
                primary_key_tuple=tuple(data['primary_key_tuple']),
                id=data.get('id'),
                metadata=data.get('metadata', {}),
                created_at=data.get('created_at'),
                updated_at=data.get('updated_at')
            )
        
        # This is raw record data
        if not primary_key_fields:
            raise ValueError("primary_key_fields must be provided when creating from raw data")
            
        # Extract the primary key tuple
        primary_key_tuple = tuple(data[pk] for pk in primary_key_fields if pk in data)
        
        return cls(
            data=data,
            primary_key_tuple=primary_key_tuple,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the record to a dictionary representation.
        
        Returns:
            A dictionary containing the record's data and metadata.
        """
        # Start with the base record data
        result = super().to_dict()
        # Add TableRecord-specific data
        result['data'] = copy.deepcopy(self.data)
        result['primary_key_tuple'] = self.primary_key_tuple
        return result
    
    def get_data_dict(self) -> Dict[str, Any]:
        """
        Get the raw data dictionary.
        
        Returns:
            A copy of the raw data dictionary.
        """
        return copy.deepcopy(self.data)
    
    def update_data(self, new_data: Dict[str, Any]) -> None:
        """
        Update the record's data.
        
        Args:
            new_data: New data to update the record with.
        """
        # Update the data
        self.data.update(new_data)
        
        # Use BaseRecord's update method to update metadata and timestamps
        super().update()
        
        # Ensure updated_at is synchronized with BaseRecord
        self.data['updated_at'] = self.updated_at
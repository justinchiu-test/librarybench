"""
Table implementation for SyncDB using the common library's storage.
"""
from typing import Dict, List, Any, Optional, Tuple, Set, Callable, Union
import copy
import time
import uuid

from common.core.storage import InMemoryStorage
from common.core.base import BaseRecord
from .schema import TableSchema
from .record import TableRecord


class Table(InMemoryStorage[TableRecord]):
    """
    A database table that stores records in memory.
    
    This implementation uses the common library's InMemoryStorage
    as the foundation for storing and querying records.
    """
    
    def __init__(self, schema: TableSchema):
        """
        Initialize a table with a schema.
        
        Args:
            schema: The schema defining the table's structure.
        """
        super().__init__()
        self.schema = schema
        
        # Map from primary key tuples to record IDs for fast lookup
        self._pk_to_id: Dict[Tuple, str] = {}
        
        # Track last modified times for records
        self.last_modified: Dict[Tuple, float] = {}
        
        # Track changes for change tracking
        self.change_log: List[Dict[str, Any]] = []
        self.index_counter = 0
        
        # Add indices for primary key fields
        for pk_field in self.schema.primary_keys:
            self.add_index(pk_field)
    
    def _get_primary_key_tuple(self, record: Dict[str, Any]) -> Tuple:
        """
        Extract primary key values as a tuple for indexing.
        
        Args:
            record: The record to extract primary key values from.
            
        Returns:
            A tuple containing the primary key values.
        """
        return tuple(record[pk] for pk in self.schema.primary_keys)
    
    def _validate_record(self, record: Dict[str, Any]) -> None:
        """
        Validate a record against the schema and raise exception if invalid.
        
        Args:
            record: The record to validate.
            
        Raises:
            ValueError: If the record is invalid.
        """
        errors = self.schema.validate_record(record)
        if errors:
            raise ValueError(f"Invalid record: {', '.join(errors)}")
    
    def _create_table_record(self, record: Dict[str, Any]) -> TableRecord:
        """
        Create a TableRecord from a dictionary.
        
        Args:
            record: The dictionary containing record data.
            
        Returns:
            A TableRecord instance.
        """
        primary_key_tuple = self._get_primary_key_tuple(record)
        return TableRecord(record, primary_key_tuple)
    
    def insert(self, record: Dict[str, Any], client_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Insert a new record into the table.
        
        Args:
            record: The record to insert.
            client_id: Optional ID of the client making the change.
            
        Returns:
            The inserted record.
            
        Raises:
            ValueError: If a record with the same primary key already exists.
        """
        self._validate_record(record)
        pk_tuple = self._get_primary_key_tuple(record)
        
        # Check if a record with this primary key already exists
        if pk_tuple in self._pk_to_id:
            raise ValueError(f"Record with primary key {pk_tuple} already exists")
        
        # Create a copy to avoid modifying the original
        stored_record = copy.deepcopy(record)
        
        # Apply default values for missing fields
        for column in self.schema.columns:
            if column.name not in stored_record and column.default is not None:
                stored_record[column.name] = column.default() if callable(column.default) else column.default
        
        # Create a TableRecord and add it to storage
        table_record = self._create_table_record(stored_record)
        record_id = super().add(table_record)
        
        # Map the primary key tuple to the record ID
        self._pk_to_id[pk_tuple] = record_id
        
        # Update last modified time
        current_time = time.time()
        self.last_modified[pk_tuple] = current_time
        
        # Record the change in the log
        self._record_change("insert", pk_tuple, None, stored_record, client_id)
        
        # Return a cleaned copy of the record
        return self._clean_record(stored_record)
    
    def update(self, record: Dict[str, Any], client_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing record in the table.
        
        Args:
            record: The record to update.
            client_id: Optional ID of the client making the change.
            
        Returns:
            The updated record.
            
        Raises:
            ValueError: If the record does not exist.
        """
        self._validate_record(record)
        pk_tuple = self._get_primary_key_tuple(record)
        
        # Check if the record exists
        if pk_tuple not in self._pk_to_id:
            raise ValueError(f"Record with primary key {pk_tuple} does not exist")
        
        # Get the record ID and the old record
        record_id = self._pk_to_id[pk_tuple]
        old_table_record = super().get(record_id)
        old_record = old_table_record.get_data_dict() if old_table_record else None
        
        # Create a copy of the new record but preserve created_at from the old record
        stored_record = copy.deepcopy(record)
        if old_record and 'created_at' in old_record:
            stored_record['created_at'] = old_record['created_at']
        
        # Create an updated TableRecord
        updated_record = self._create_table_record(stored_record)
        
        # Use InMemoryStorage's functionality to update the record
        # This will automatically handle index updates
        self._records[record_id] = updated_record
        
        # Use InMemoryStorage's update indices to ensure all indices are updated correctly
        for index in self._indices.values():
            index.update(old_table_record, updated_record)
        
        # Update last modified time
        current_time = time.time()
        self.last_modified[pk_tuple] = current_time
        
        # Record the change in the log
        self._record_change("update", pk_tuple, old_record, stored_record, client_id)
        
        # Return a cleaned copy of the record
        return self._clean_record(stored_record)
    
    def delete(self, primary_key_values: List[Any], client_id: Optional[str] = None) -> None:
        """
        Delete a record from the table by its primary key values.
        
        Args:
            primary_key_values: The values for the primary key columns.
            client_id: Optional ID of the client making the change.
            
        Raises:
            ValueError: If the record does not exist.
        """
        pk_tuple = tuple(primary_key_values)
        
        # Check if the record exists
        if pk_tuple not in self._pk_to_id:
            raise ValueError(f"Record with primary key {pk_tuple} does not exist")
        
        # Get the record ID and the old record
        record_id = self._pk_to_id[pk_tuple]
        old_table_record = self.get(record_id)
        old_record = old_table_record.get_data_dict() if old_table_record else None
        
        # Delete the record from storage
        super().delete(record_id)
        
        # Remove the primary key mapping
        del self._pk_to_id[pk_tuple]
        
        # Remove from last modified
        if pk_tuple in self.last_modified:
            del self.last_modified[pk_tuple]
        
        # Record the change in the log
        self._record_change("delete", pk_tuple, old_record, None, client_id)
    
    def get(self, id_or_values: Union[str, List[Any]]) -> Optional[TableRecord]:
        """
        Get a record by its ID or primary key values.
        
        Args:
            id_or_values: The ID of the record or primary key values list.
            
        Returns:
            The record if found, None otherwise.
        """
        # If id_or_values is a string, it's an ID
        if isinstance(id_or_values, str):
            return super().get(id_or_values)
        
        # Otherwise, it's primary key values
        pk_tuple = tuple(id_or_values)
        
        # Check if the record exists
        if pk_tuple not in self._pk_to_id:
            return None
        
        # Get the record ID and the record
        record_id = self._pk_to_id[pk_tuple]
        return super().get(record_id)
    
    def get_dict(self, primary_key_values: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Get a record as a dictionary by its primary key values.
        
        Args:
            primary_key_values: The values for the primary key columns.
            
        Returns:
            The record dictionary if found, None otherwise.
        """
        record = self.get(primary_key_values)
        if record:
            return self._clean_record(record.get_data_dict())
        return None
    
    def query(self, 
              conditions: Optional[Dict[str, Any]] = None, 
              limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Query records that match the given conditions.
        
        Args:
            conditions: Dictionary of column name to value that records must match.
            limit: Maximum number of records to return.
            
        Returns:
            List of matching records.
        """
        # If no conditions, return all records (up to the limit)
        if conditions is None:
            records = [record.get_data_dict() for record in self._records.values()]
            cleaned_records = [self._clean_record(record) for record in records]
            if limit is not None:
                cleaned_records = cleaned_records[:limit]
            return cleaned_records
        
        # Check if we can use an index for one of the conditions
        indexed_field = next((field for field in conditions.keys() if field in self._indices), None)
        
        matching_records = []
        if indexed_field:
            # Use index for the first condition
            value = conditions[indexed_field]
            record_ids = self._indices[indexed_field].find(value)
            
            # Get the records that match the indexed field
            filtered_records = [self._records[record_id] for record_id in record_ids if record_id in self._records]
            
            # If there are additional conditions, use the common filter method
            if len(conditions) > 1:
                # Create a predicate function to match remaining conditions
                def predicate(record: TableRecord) -> bool:
                    record_data = record.get_data_dict()
                    for col_name, expected_value in conditions.items():
                        if col_name != indexed_field:  # Skip the indexed field we already filtered on
                            if col_name not in record_data or record_data[col_name] != expected_value:
                                return False
                    return True
                
                # Use InMemoryStorage's filter method with our custom predicate
                filtered_records = self.filter(predicate)
            
            matching_records = filtered_records
            
            # Apply limit if needed
            if limit is not None and len(matching_records) > limit:
                matching_records = matching_records[:limit]
        else:
            # Use InMemoryStorage's filter method with a predicate for all conditions
            def predicate(record: TableRecord) -> bool:
                return self._matches_conditions(record.get_data_dict(), conditions)
            
            matching_records = self.filter(predicate)
            
            # Apply limit if needed
            if limit is not None and len(matching_records) > limit:
                matching_records = matching_records[:limit]
        
        # Convert records to dictionaries and clean them
        return [self._clean_record(record.get_data_dict()) for record in matching_records]
    
    def _clean_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove internal fields from a record if they're not part of the schema.
        
        Args:
            record: The record to clean.
            
        Returns:
            A cleaned copy of the record.
        """
        result = copy.deepcopy(record)
        # Remove internal timestamps if they're not part of the schema
        if 'updated_at' in result and not self.schema.get_column('updated_at'):
            del result['updated_at']
        if 'created_at' in result and not self.schema.get_column('created_at'):
            del result['created_at']
        return result
    
    def _matches_conditions(self, record: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """
        Check if a record matches all the given conditions.
        
        Args:
            record: The record to check.
            conditions: The conditions to match.
            
        Returns:
            True if the record matches all conditions, False otherwise.
        """
        for col_name, expected_value in conditions.items():
            if col_name not in record or record[col_name] != expected_value:
                return False
        return True
    
    def _record_change(self, 
                      operation: str, 
                      pk_tuple: Tuple, 
                      old_record: Optional[Dict[str, Any]], 
                      new_record: Optional[Dict[str, Any]],
                      client_id: Optional[str] = None) -> None:
        """
        Record a change in the change log.
        
        Args:
            operation: The operation performed (insert, update, delete).
            pk_tuple: The primary key tuple of the affected record.
            old_record: The old version of the record (None for inserts).
            new_record: The new version of the record (None for deletes).
            client_id: Optional ID of the client making the change.
        """
        self.index_counter += 1
        change = {
            "id": self.index_counter,
            "operation": operation,
            "primary_key": pk_tuple,
            "timestamp": time.time(),
            "old_record": old_record,
            "new_record": new_record,
            "client_id": client_id or "server"
        }
        self.change_log.append(change)
    
    def get_changes_since(self, index: int) -> List[Dict[str, Any]]:
        """
        Get all changes that occurred after the given index.
        
        Args:
            index: The index to get changes after.
            
        Returns:
            List of changes.
        """
        return [change for change in self.change_log if change["id"] > index]
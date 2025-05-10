"""Core database engine for MobileSyncDB."""

import time
import uuid
import copy
import json
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from datetime import datetime
from dataclasses import dataclass, field

from .exceptions import (
    TableAlreadyExistsError,
    TableNotFoundError,
    RecordNotFoundError,
    SchemaValidationError,
    IndexError,
)


class ColumnType:
    """Valid column data types for the database."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    JSON = "json"
    BINARY = "binary"

    @classmethod
    def validate(cls, value: Any, type_name: str) -> bool:
        """Validate that a value matches the expected type."""
        if type_name == cls.STRING:
            return isinstance(value, str)
        elif type_name == cls.INTEGER:
            return isinstance(value, int) and not isinstance(value, bool)
        elif type_name == cls.FLOAT:
            return isinstance(value, float)
        elif type_name == cls.BOOLEAN:
            return isinstance(value, bool)
        elif type_name == cls.DATETIME:
            # Accept datetime objects or ISO8601 strings
            if isinstance(value, datetime):
                return True
            elif isinstance(value, str):
                try:
                    datetime.fromisoformat(value.replace("Z", "+00:00"))
                    return True
                except ValueError:
                    return False
            return False
        elif type_name == cls.JSON:
            # Accept dict, list, or JSON serializable types
            if isinstance(value, (dict, list)):
                return True
            try:
                json.dumps(value)
                return True
            except (TypeError, ValueError):
                return False
        elif type_name == cls.BINARY:
            return isinstance(value, bytes)
        return False

    @classmethod
    def convert(cls, value: Any, type_name: str) -> Any:
        """Convert a value to the specified type if possible."""
        if type_name == cls.STRING:
            return str(value)
        elif type_name == cls.INTEGER:
            return int(value)
        elif type_name == cls.FLOAT:
            return float(value)
        elif type_name == cls.BOOLEAN:
            return bool(value)
        elif type_name == cls.DATETIME:
            if isinstance(value, datetime):
                return value
            elif isinstance(value, str):
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            raise ValueError(f"Cannot convert {value} to datetime")
        elif type_name == cls.JSON:
            if isinstance(value, str):
                return json.loads(value)
            return value
        elif type_name == cls.BINARY:
            if isinstance(value, str):
                return value.encode("utf-8")
            return bytes(value)
        return value


@dataclass
class SchemaField:
    """Defines a field in a table schema."""

    name: str
    data_type: str
    nullable: bool = False
    default: Any = None
    is_primary_key: bool = False
    is_indexed: bool = False


@dataclass
class TableSchema:
    """Defines the schema for a database table."""

    name: str
    fields: Dict[str, SchemaField]
    primary_key: str
    version: int = 1
    indexes: Set[str] = field(default_factory=set)


@dataclass
class Record:
    """Represents a record in the database with version control information."""

    data: Dict[str, Any]
    created_at: float
    updated_at: float
    version: int = 1
    client_id: Optional[str] = None
    is_deleted: bool = False
    conflict_info: Optional[Dict[str, Any]] = None


class Table:
    """Represents a table in the database."""

    def __init__(self, schema: TableSchema):
        """Initialize a table with the given schema."""
        self.schema = schema
        self.data: Dict[str, Record] = {}
        self.indexes: Dict[str, Dict[Any, Set[str]]] = {}
        
        # Create indexes for the primary key and any other indexed fields
        self._create_index(schema.primary_key)
        for field_name in schema.indexes:
            self._create_index(field_name)

    def _create_index(self, field_name: str) -> None:
        """Create an index for the specified field."""
        if field_name not in self.schema.fields:
            raise IndexError(f"Cannot create index: field '{field_name}' does not exist")
        
        self.indexes[field_name] = {}
        self.schema.indexes.add(field_name)
        
        # Populate the index with existing data
        for pk, record in self.data.items():
            if field_name in record.data and not record.is_deleted:
                value = record.data[field_name]
                if value not in self.indexes[field_name]:
                    self.indexes[field_name][value] = set()
                self.indexes[field_name][value].add(pk)

    def _drop_index(self, field_name: str) -> None:
        """Drop an index for the specified field."""
        if field_name == self.schema.primary_key:
            raise IndexError("Cannot drop index on primary key")
        
        if field_name in self.indexes:
            del self.indexes[field_name]
            self.schema.indexes.remove(field_name)

    def _update_indexes(self, pk: str, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> None:
        """Update indexes when a record is modified."""
        for field_name in self.indexes:
            if field_name in old_data and field_name in new_data:
                old_value = old_data[field_name]
                new_value = new_data[field_name]
                
                # If the value has changed, update the index
                if old_value != new_value:
                    # Remove from old index
                    if old_value in self.indexes[field_name]:
                        self.indexes[field_name][old_value].discard(pk)
                        if not self.indexes[field_name][old_value]:
                            del self.indexes[field_name][old_value]
                    
                    # Add to new index
                    if new_value not in self.indexes[field_name]:
                        self.indexes[field_name][new_value] = set()
                    self.indexes[field_name][new_value].add(pk)
            
            elif field_name in old_data:
                # Field was removed, remove from index
                old_value = old_data[field_name]
                if old_value in self.indexes[field_name]:
                    self.indexes[field_name][old_value].discard(pk)
                    if not self.indexes[field_name][old_value]:
                        del self.indexes[field_name][old_value]
            
            elif field_name in new_data:
                # Field was added, add to index
                new_value = new_data[field_name]
                if new_value not in self.indexes[field_name]:
                    self.indexes[field_name][new_value] = set()
                self.indexes[field_name][new_value].add(pk)

    def _validate_record(self, data: Dict[str, Any], check_primary_key: bool = True) -> None:
        """Validate that a record conforms to the table schema."""
        # Check that primary key is present
        if check_primary_key and self.schema.primary_key not in data:
            raise SchemaValidationError(f"Primary key '{self.schema.primary_key}' is required")
        
        # Check that all fields conform to their defined types
        for field_name, value in data.items():
            if field_name not in self.schema.fields:
                raise SchemaValidationError(f"Unknown field '{field_name}'")
            
            field_schema = self.schema.fields[field_name]
            if value is None:
                if not field_schema.nullable:
                    raise SchemaValidationError(f"Field '{field_name}' cannot be null")
            else:
                if not ColumnType.validate(value, field_schema.data_type):
                    raise SchemaValidationError(
                        f"Field '{field_name}' with value '{value}' does not match type '{field_schema.data_type}'"
                    )
        
        # Check that all required fields are present
        for field_name, field_schema in self.schema.fields.items():
            if field_name not in data:
                if not field_schema.nullable and field_schema.default is None:
                    raise SchemaValidationError(f"Required field '{field_name}' is missing")

    def _apply_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values for fields not provided in the data."""
        result = data.copy()
        
        for field_name, field_schema in self.schema.fields.items():
            if field_name not in result:
                if field_schema.default is not None:
                    result[field_name] = field_schema.default
        
        return result

    def insert(self, data: Dict[str, Any], client_id: Optional[str] = None) -> str:
        """Insert a new record into the table."""
        # Validate record against schema
        self._validate_record(data)
        
        # Apply defaults for missing fields
        complete_data = self._apply_defaults(data)
        
        # Get primary key
        pk = str(complete_data[self.schema.primary_key])
        
        # Check if record already exists
        if pk in self.data and not self.data[pk].is_deleted:
            raise ValueError(f"Record with primary key '{pk}' already exists")
        
        # Create record with metadata
        now = time.time()
        record = Record(
            data=complete_data,
            created_at=now,
            updated_at=now,
            version=1,
            client_id=client_id,
        )
        
        # Store the record
        self.data[pk] = record
        
        # Update indexes
        for field_name in self.indexes:
            if field_name in complete_data:
                value = complete_data[field_name]
                if value not in self.indexes[field_name]:
                    self.indexes[field_name][value] = set()
                self.indexes[field_name][value].add(pk)
        
        return pk

    def get(self, pk: str) -> Dict[str, Any]:
        """Retrieve a record by its primary key."""
        if pk not in self.data or self.data[pk].is_deleted:
            raise RecordNotFoundError(f"Record with primary key '{pk}' not found")
        
        return copy.deepcopy(self.data[pk].data)

    def get_with_metadata(self, pk: str) -> Record:
        """Retrieve a record with its metadata by primary key."""
        if pk not in self.data or self.data[pk].is_deleted:
            raise RecordNotFoundError(f"Record with primary key '{pk}' not found")
        
        return copy.deepcopy(self.data[pk])

    def update(
        self, 
        pk: str, 
        data: Dict[str, Any], 
        client_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing record."""
        if pk not in self.data or self.data[pk].is_deleted:
            raise RecordNotFoundError(f"Record with primary key '{pk}' not found")
        
        # Validate that we're not trying to change the primary key
        if self.schema.primary_key in data and str(data[self.schema.primary_key]) != pk:
            raise SchemaValidationError("Cannot change primary key of a record")
        
        # Validate the update data
        self._validate_record(data, check_primary_key=False)
        
        # Get the current record
        record = self.data[pk]
        old_data = record.data.copy()
        
        # Update the record data
        new_data = old_data.copy()
        new_data.update(data)
        
        # Update record metadata
        record.data = new_data
        record.updated_at = time.time()
        record.version += 1
        record.client_id = client_id
        
        # Update indexes
        self._update_indexes(pk, old_data, new_data)
        
        return copy.deepcopy(new_data)

    def delete(self, pk: str, client_id: Optional[str] = None) -> None:
        """Delete a record by marking it as deleted."""
        if pk not in self.data or self.data[pk].is_deleted:
            raise RecordNotFoundError(f"Record with primary key '{pk}' not found")
        
        record = self.data[pk]
        old_data = record.data.copy()
        
        # Mark as deleted and update metadata
        record.is_deleted = True
        record.updated_at = time.time()
        record.version += 1
        record.client_id = client_id
        
        # Remove from indexes
        for field_name in self.indexes:
            if field_name in old_data:
                value = old_data[field_name]
                if value in self.indexes[field_name]:
                    self.indexes[field_name][value].discard(pk)
                    if not self.indexes[field_name][value]:
                        del self.indexes[field_name][value]

    def find(
        self, 
        conditions: Dict[str, Any], 
        limit: Optional[int] = None,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[Dict[str, Any]]:
        """Find records that match the given conditions."""
        results = []
        filtered_pks = self._find_matching_primary_keys(conditions)
        
        # Apply offset and limit
        paginated_pks = filtered_pks[offset:None if limit is None else offset + limit]
        
        # Get the actual records
        for pk in paginated_pks:
            record = self.data[pk]
            if not record.is_deleted or include_deleted:
                results.append(copy.deepcopy(record.data))
        
        return results

    def _find_matching_primary_keys(self, conditions: Dict[str, Any]) -> List[str]:
        """Find primary keys of records that match the given conditions."""
        if not conditions:
            # If no conditions, return all non-deleted records
            return [pk for pk, record in self.data.items() if not record.is_deleted]
        
        # Find the most selective indexed condition to start with
        candidate_pks = None
        for field_name, value in conditions.items():
            if field_name in self.indexes:
                if value in self.indexes[field_name]:
                    matching_pks = self.indexes[field_name][value]
                    if candidate_pks is None or len(matching_pks) < len(candidate_pks):
                        candidate_pks = matching_pks.copy()
        
        # If no indexed fields matched, we need to scan all records
        if candidate_pks is None:
            candidate_pks = {pk for pk, record in self.data.items() if not record.is_deleted}
        
        # Filter by the remaining conditions
        result = []
        for pk in candidate_pks:
            record = self.data[pk]
            if not record.is_deleted:
                matches = True
                for field_name, value in conditions.items():
                    if field_name not in record.data or record.data[field_name] != value:
                        matches = False
                        break
                if matches:
                    result.append(pk)
        
        return result

    def count(self, conditions: Optional[Dict[str, Any]] = None) -> int:
        """Count the number of records matching the given conditions."""
        if conditions is None:
            return sum(1 for record in self.data.values() if not record.is_deleted)
        
        return len(self._find_matching_primary_keys(conditions))

    def get_changes_since(
        self, 
        timestamp: float, 
        client_id: Optional[str] = None
    ) -> List[Tuple[str, Record]]:
        """Get all records that have changed since the specified timestamp."""
        changes = []
        for pk, record in self.data.items():
            # Include records that were updated after the timestamp
            # If client_id is provided, exclude changes made by that client
            if record.updated_at > timestamp and (client_id is None or record.client_id != client_id):
                changes.append((pk, copy.deepcopy(record)))
        
        # Sort changes by updated_at timestamp
        return sorted(changes, key=lambda x: x[1].updated_at)

    def get_all(
        self, 
        limit: Optional[int] = None,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all records, with optional pagination."""
        results = []
        
        # Get all record primary keys, sorted by creation time
        pks = sorted(
            self.data.keys(),
            key=lambda pk: self.data[pk].created_at
        )
        
        # Apply offset and limit
        paginated_pks = pks[offset:None if limit is None else offset + limit]
        
        # Get the actual records
        for pk in paginated_pks:
            record = self.data[pk]
            if not record.is_deleted or include_deleted:
                results.append(copy.deepcopy(record.data))
        
        return results

    def truncate(self) -> None:
        """Remove all records from the table."""
        self.data.clear()
        
        # Clear indexes
        for field_name in self.indexes:
            self.indexes[field_name].clear()


class MobileDBEngine:
    """Core in-memory database engine for MobileSyncDB."""

    def __init__(self, max_memory_mb: Optional[int] = None):
        """Initialize the database engine."""
        self.tables: Dict[str, Table] = {}
        self.schema_versions: Dict[str, List[TableSchema]] = {}
        self.max_memory_bytes = None if max_memory_mb is None else max_memory_mb * 1024 * 1024
        self._client_sessions: Dict[str, Dict[str, Any]] = {}

    def create_table(
        self, 
        name: str, 
        schema: Dict[str, str], 
        primary_key: str,
        nullable_fields: Optional[List[str]] = None,
        default_values: Optional[Dict[str, Any]] = None,
        indexes: Optional[List[str]] = None
    ) -> None:
        """Create a new table with the specified schema."""
        if name in self.tables:
            raise TableAlreadyExistsError(f"Table '{name}' already exists")
        
        if primary_key not in schema:
            raise SchemaValidationError(f"Primary key '{primary_key}' not in schema")
        
        # Set up nullable fields and defaults
        nullable_fields = nullable_fields or []
        default_values = default_values or {}
        indexes = indexes or []
        
        # Create schema fields
        fields = {}
        for field_name, field_type in schema.items():
            fields[field_name] = SchemaField(
                name=field_name,
                data_type=field_type,
                nullable=field_name in nullable_fields,
                default=default_values.get(field_name),
                is_primary_key=field_name == primary_key,
                is_indexed=field_name in indexes or field_name == primary_key
            )
        
        # Create table schema
        table_schema = TableSchema(
            name=name,
            fields=fields,
            primary_key=primary_key,
            indexes=set(indexes + [primary_key])
        )
        
        # Create the table
        self.tables[name] = Table(table_schema)
        
        # Store schema version history
        self.schema_versions[name] = [table_schema]

    def drop_table(self, name: str) -> None:
        """Drop a table from the database."""
        if name not in self.tables:
            raise TableNotFoundError(f"Table '{name}' not found")
        
        del self.tables[name]
        del self.schema_versions[name]

    def get_table(self, name: str) -> Table:
        """Get a table by name."""
        if name not in self.tables:
            raise TableNotFoundError(f"Table '{name}' not found")
        
        return self.tables[name]

    def table_exists(self, name: str) -> bool:
        """Check if a table exists."""
        return name in self.tables

    def insert(
        self, 
        table_name: str, 
        data: Dict[str, Any], 
        client_id: Optional[str] = None
    ) -> str:
        """Insert a record into a table."""
        table = self.get_table(table_name)
        return table.insert(data, client_id)

    def get(self, table_name: str, pk: str) -> Dict[str, Any]:
        """Get a record from a table by primary key."""
        table = self.get_table(table_name)
        return table.get(pk)

    def update(
        self, 
        table_name: str, 
        pk: str, 
        data: Dict[str, Any], 
        client_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a record in a table."""
        table = self.get_table(table_name)
        return table.update(pk, data, client_id)

    def delete(
        self, 
        table_name: str, 
        pk: str,
        client_id: Optional[str] = None
    ) -> None:
        """Delete a record from a table."""
        table = self.get_table(table_name)
        table.delete(pk, client_id)

    def find(
        self, 
        table_name: str, 
        conditions: Dict[str, Any], 
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Find records in a table matching the given conditions."""
        table = self.get_table(table_name)
        return table.find(conditions, limit, offset)

    def get_all(
        self, 
        table_name: str, 
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all records from a table."""
        table = self.get_table(table_name)
        return table.get_all(limit, offset)

    def count(
        self, 
        table_name: str, 
        conditions: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records in a table."""
        table = self.get_table(table_name)
        return table.count(conditions)

    def truncate_table(self, table_name: str) -> None:
        """Remove all records from a table."""
        table = self.get_table(table_name)
        table.truncate()

    def add_index(self, table_name: str, field_name: str) -> None:
        """Add an index to a table."""
        table = self.get_table(table_name)
        table._create_index(field_name)

    def drop_index(self, table_name: str, field_name: str) -> None:
        """Drop an index from a table."""
        table = self.get_table(table_name)
        table._drop_index(field_name)

    def get_changes_since(
        self, 
        table_name: str, 
        timestamp: float, 
        client_id: Optional[str] = None
    ) -> List[Tuple[str, Record]]:
        """Get changes to a table since the specified timestamp."""
        table = self.get_table(table_name)
        return table.get_changes_since(timestamp, client_id)

    def register_client(
        self, 
        client_id: str,
        sync_state: Optional[Dict[str, float]] = None
    ) -> None:
        """Register a client for tracking sync state."""
        if sync_state is None:
            sync_state = {}
        
        self._client_sessions[client_id] = {
            "id": client_id,
            "last_sync": time.time(),
            "table_sync_state": sync_state,
            "connected_at": time.time()
        }

    def update_client_sync_state(
        self, 
        client_id: str, 
        table_name: str, 
        sync_timestamp: float
    ) -> None:
        """Update the sync state for a client."""
        if client_id not in self._client_sessions:
            self.register_client(client_id)
        
        self._client_sessions[client_id]["last_sync"] = time.time()
        self._client_sessions[client_id]["table_sync_state"][table_name] = sync_timestamp

    def get_client_sync_state(
        self, 
        client_id: str, 
        table_name: Optional[str] = None
    ) -> Union[Dict[str, float], float, None]:
        """Get the sync state for a client."""
        if client_id not in self._client_sessions:
            return None
        
        if table_name is None:
            return self._client_sessions[client_id]["table_sync_state"]
        
        return self._client_sessions[client_id]["table_sync_state"].get(table_name, 0.0)

    def get_client_session(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get the session information for a client."""
        return self._client_sessions.get(client_id)
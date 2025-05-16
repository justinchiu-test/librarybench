"""
Core in-memory database engine implementation.
"""
from typing import Dict, List, Any, Optional, Tuple, Callable, Set, Union
import copy
import time
import uuid
import json

from common.core.serialization import Serializable
from common.core.storage import InMemoryStorage
from .schema import DatabaseSchema, TableSchema, schema_registry
from .table import Table
from .record import TableRecord


class Transaction:
    """
    Manages a database transaction.
    """
    def __init__(self, database: 'Database'):
        self.database = database
        self.tables_snapshot: Dict[str, Dict[Tuple, Dict[str, Any]]] = {}
        self.operations: List[Tuple[str, str, Dict[str, Any]]] = []
        self.committed = False
        self.rolled_back = False
    
    def __enter__(self):
        """Begin the transaction by creating snapshots of tables."""
        for table_name, table in self.database.tables.items():
            # Create a snapshot of the table's state
            self.tables_snapshot[table_name] = {}
            for pk_tuple, record_id in table._pk_to_id.items():
                table_record = table._records.get(record_id)
                if table_record:
                    self.tables_snapshot[table_name][pk_tuple] = copy.deepcopy(table_record.get_data_dict())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Rollback the transaction if not committed and an exception occurred."""
        if exc_type is not None and not self.committed and not self.rolled_back:
            self.rollback()
        return False  # Don't suppress exceptions
    
    def insert(self, table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a record as part of this transaction."""
        if self.committed or self.rolled_back:
            raise ValueError("Transaction already completed")

        result = self.database.insert(table_name, record, client_id="transaction")
        self.operations.append(("insert", table_name, copy.deepcopy(record)))
        return result

    def update(self, table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record as part of this transaction."""
        if self.committed or self.rolled_back:
            raise ValueError("Transaction already completed")

        result = self.database.update(table_name, record, client_id="transaction")
        self.operations.append(("update", table_name, copy.deepcopy(record)))
        return result

    def delete(self, table_name: str, primary_key_values: List[Any]) -> None:
        """Delete a record as part of this transaction."""
        if self.committed or self.rolled_back:
            raise ValueError("Transaction already completed")

        self.database.delete(table_name, primary_key_values, client_id="transaction")
        self.operations.append(("delete", table_name, {"primary_key_values": primary_key_values}))
    
    def commit(self) -> None:
        """Commit the transaction."""
        if self.committed or self.rolled_back:
            raise ValueError("Transaction already completed")
        
        self.committed = True
        # All changes have already been applied to the database tables
        # We just need to mark the transaction as committed
    
    def rollback(self) -> None:
        """Roll back the transaction."""
        if self.committed or self.rolled_back:
            raise ValueError("Transaction already completed")

        # Step 1: Remove any newly added records
        for op_type, table_name, data in self.operations:
            if op_type == "insert":
                # For inserts, we need to remove the record
                table = self.database.tables.get(table_name)
                if table:
                    # Extract the primary key to identify the record
                    primary_keys = self.database.schema.tables[table_name].primary_keys
                    pk_values = [data[pk_name] for pk_name in primary_keys if pk_name in data]
                    if pk_values:
                        pk_tuple = tuple(pk_values)
                        # Remove the record that was inserted
                        if pk_tuple in table._pk_to_id:
                            table.delete(pk_values, client_id="transaction_rollback")

        # Step 2: Restore previous state for updated records
        for table_name, records_snapshot in self.tables_snapshot.items():
            table = self.database.tables[table_name]
            # Restore all records from the snapshot
            for pk_tuple, record in records_snapshot.items():
                if pk_tuple in table._pk_to_id:
                    # Update to the original state
                    table.update(record, client_id="transaction_rollback")
                else:
                    # Record was deleted, reinsert it
                    table.insert(record, client_id="transaction_rollback")

        # Step 3: Remove transaction changes from change logs
        for table_name in self.database.tables:
            table = self.database.tables[table_name]
            # Remove changes with this transaction's client ID
            original_length = len(table.change_log)
            table.change_log = [
                change for change in table.change_log
                if change.get("client_id") not in ["transaction", "transaction_rollback"]
            ]
            # If we removed changes, reset the index counter
            if len(table.change_log) < original_length:
                table.index_counter = max([0] + [c.get("id", 0) for c in table.change_log])

        self.rolled_back = True


class Database(Serializable):
    """
    An in-memory database that stores tables and supports transactions.
    """
    def __init__(self, schema: DatabaseSchema):
        self.schema = schema
        self.tables: Dict[str, Table] = {}
        self.created_at = time.time()
        self.updated_at = self.created_at
        self.metadata: Dict[str, Any] = {}

        # Create tables based on the schema
        for table_name, table_schema in schema.tables.items():
            self._create_table(table_schema)
            
        # Register all schemas with the global schema registry
        self.schema.register_with_registry(schema_registry)

    def _create_table(self, table_schema: TableSchema) -> Table:
        """Create a new table based on the schema."""
        table = Table(table_schema)
        self.tables[table_schema.name] = table
        return table
    
    def _get_table(self, table_name: str) -> Table:
        """Get a table by name or raise an exception if it doesn't exist."""
        table = self.tables.get(table_name)
        if table is None:
            raise ValueError(f"Table {table_name} does not exist")
        return table
    
    def insert(self, 
              table_name: str, 
              record: Dict[str, Any], 
              client_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Insert a record into a table.
        
        Args:
            table_name: The name of the table
            record: The record to insert
            client_id: Optional ID of the client making the change
            
        Returns:
            The inserted record
        """
        table = self._get_table(table_name)
        self.updated_at = time.time()
        return table.insert(record, client_id)
    
    def update(self, 
              table_name: str, 
              record: Dict[str, Any], 
              client_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a record in a table.
        
        Args:
            table_name: The name of the table
            record: The record to update (must include primary key)
            client_id: Optional ID of the client making the change
            
        Returns:
            The updated record
        """
        table = self._get_table(table_name)
        self.updated_at = time.time()
        return table.update(record, client_id)
    
    def delete(self, 
              table_name: str, 
              primary_key_values: List[Any], 
              client_id: Optional[str] = None) -> None:
        """
        Delete a record from a table.
        
        Args:
            table_name: The name of the table
            primary_key_values: The values for the primary key columns
            client_id: Optional ID of the client making the change
        """
        table = self._get_table(table_name)
        self.updated_at = time.time()
        table.delete(primary_key_values, client_id)
    
    def get(self, table_name: str, primary_key_values: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Get a record from a table by its primary key.
        
        Args:
            table_name: The name of the table
            primary_key_values: The values for the primary key columns
            
        Returns:
            The record if found, None otherwise
        """
        table = self._get_table(table_name)
        return table.get_dict(primary_key_values)
    
    def query(self, 
             table_name: str, 
             conditions: Optional[Dict[str, Any]] = None, 
             limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Query records from a table.
        
        Args:
            table_name: The name of the table
            conditions: Optional conditions that records must match
            limit: Optional maximum number of records to return
            
        Returns:
            List of matching records
        """
        table = self._get_table(table_name)
        return table.query(conditions, limit)
    
    def begin_transaction(self) -> Transaction:
        """Begin a new transaction."""
        return Transaction(self)
    
    def get_changes_since(self, table_name: str, index: int) -> List[Dict[str, Any]]:
        """
        Get all changes to a table since the given index.
        
        Args:
            table_name: The name of the table
            index: The index to get changes after
            
        Returns:
            List of changes
        """
        table = self._get_table(table_name)
        return table.get_changes_since(index)
    
    def generate_client_id(self) -> str:
        """Generate a unique client ID."""
        return str(uuid.uuid4())
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the database.
        
        Args:
            key: The metadata key
            value: The metadata value
        """
        self.metadata[key] = value
        self.updated_at = time.time()
    
    def get_metadata(self, key: str) -> Optional[Any]:
        """
        Get metadata from the database.
        
        Args:
            key: The metadata key
            
        Returns:
            The metadata value if found, None otherwise
        """
        return self.metadata.get(key)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the database to a dictionary representation for serialization.
        
        Returns:
            A dictionary containing the database's metadata and schema.
        """
        return {
            'schema': self.schema.to_dict(),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Database':
        """
        Create a database from a dictionary representation.
        
        Args:
            data: Dictionary containing database data.
        
        Returns:
            A new Database instance.
        """
        schema = DatabaseSchema.from_dict(data['schema'])
        db = cls(schema)
        db.created_at = data.get('created_at', time.time())
        db.updated_at = data.get('updated_at', db.created_at)
        db.metadata = data.get('metadata', {})
        return db
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save the database schema and metadata to a file.
        
        Args:
            file_path: The path to save the database to.
        """
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Database':
        """
        Load a database from a file.
        
        Args:
            file_path: The path to load the database from.
            
        Returns:
            A new Database instance.
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
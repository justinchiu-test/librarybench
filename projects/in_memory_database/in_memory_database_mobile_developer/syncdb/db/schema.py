"""
Schema definition for SyncDB tables.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Type


@dataclass
class Column:
    """Defines a column in a database table."""
    name: str
    data_type: Type
    primary_key: bool = False
    nullable: bool = True
    default: Optional[Any] = None
    
    def validate_value(self, value: Any) -> bool:
        """Validate that a value matches the column's type."""
        if value is None:
            return self.nullable
        
        # Check if the value is of the expected data type
        try:
            if not isinstance(value, self.data_type):
                # Try to convert the value to the expected type
                converted_value = self.data_type(value)
                return True
            return True
        except (ValueError, TypeError):
            return False


@dataclass
class TableSchema:
    """Defines the schema for a database table."""
    name: str
    columns: List[Column]
    version: int = 1
    _column_dict: Dict[str, Column] = field(default_factory=dict, init=False)
    
    def __post_init__(self) -> None:
        """Process columns after initialization."""
        # Build a dictionary of columns by name for faster access
        self._column_dict = {col.name: col for col in self.columns}
        
        # Ensure there's at least one primary key
        primary_keys = [col for col in self.columns if col.primary_key]
        if not primary_keys:
            raise ValueError(f"Table {self.name} must have at least one primary key column")
    
    @property
    def primary_keys(self) -> List[str]:
        """Return the names of primary key columns."""
        return [col.name for col in self.columns if col.primary_key]
    
    def get_column(self, name: str) -> Optional[Column]:
        """Get a column by name."""
        return self._column_dict.get(name)
    
    def validate_record(self, record: Dict[str, Any]) -> List[str]:
        """
        Validate a record against the schema.
        Returns a list of error messages, empty if valid.
        """
        errors = []
        
        # Check that all primary keys are present
        for pk in self.primary_keys:
            if pk not in record:
                errors.append(f"Missing primary key {pk}")
        
        # Check that all provided values are valid
        for field_name, value in record.items():
            column = self.get_column(field_name)
            if not column:
                errors.append(f"Unknown column {field_name}")
                continue
            
            if not column.validate_value(value):
                errors.append(f"Invalid value for {field_name}, expected {column.data_type.__name__}")
        
        return errors


@dataclass
class DatabaseSchema:
    """Defines the schema for the entire database."""
    tables: Dict[str, TableSchema]
    version: int = 1
    
    def get_table(self, name: str) -> Optional[TableSchema]:
        """Get a table schema by name."""
        return self.tables.get(name)
    
    def add_table(self, table: TableSchema) -> None:
        """Add a table to the schema."""
        self.tables[table.name] = table
"""
Schema definition for SyncDB tables.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Type

from common.core import Schema, SchemaField, FieldType


@dataclass
class Column:
    """Defines a column in a database table."""
    name: str
    data_type: Type
    primary_key: bool = False
    nullable: bool = True
    default: Optional[Any] = None
    
    def to_schema_field(self) -> SchemaField:
        """Convert to a SchemaField from the common library."""
        # Map Python types to FieldType
        field_type = FieldType.ANY
        if self.data_type == str:
            field_type = FieldType.STRING
        elif self.data_type == int:
            field_type = FieldType.INTEGER
        elif self.data_type == float:
            field_type = FieldType.FLOAT
        elif self.data_type == bool:
            field_type = FieldType.BOOLEAN
        elif self.data_type == list:
            field_type = FieldType.ARRAY
        elif self.data_type == dict:
            field_type = FieldType.OBJECT
        
        # Create constraints dictionary
        constraints = {}
        if self.primary_key:
            constraints["primary_key"] = True
        
        return SchemaField(
            name=self.name,
            field_type=field_type,
            required=not self.nullable,
            nullable=self.nullable,
            default=self.default,
            constraints=constraints
        )
    
    @classmethod
    def from_schema_field(cls, field: SchemaField) -> 'Column':
        """Create a Column from a SchemaField."""
        # Map FieldType to Python types
        data_type: Type = Any
        if field.field_type == FieldType.STRING:
            data_type = str
        elif field.field_type == FieldType.INTEGER:
            data_type = int
        elif field.field_type == FieldType.FLOAT:
            data_type = float
        elif field.field_type == FieldType.BOOLEAN:
            data_type = bool
        elif field.field_type == FieldType.ARRAY:
            data_type = list
        elif field.field_type == FieldType.OBJECT:
            data_type = dict
        
        # Check if this is a primary key
        primary_key = False
        if field.constraints and "primary_key" in field.constraints:
            primary_key = field.constraints["primary_key"]
        
        return cls(
            name=field.name,
            data_type=data_type,
            primary_key=primary_key,
            nullable=field.nullable,
            default=field.default
        )
    
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
    
    def to_schema(self) -> Schema:
        """Convert to a Schema from the common library."""
        fields = [col.to_schema_field() for col in self.columns]
        return Schema(
            name=self.name,
            fields=fields,
            version=str(self.version),
            description=f"SyncDB table schema for {self.name}",
            additional_properties=False
        )
    
    @classmethod
    def from_schema(cls, schema: Schema) -> 'TableSchema':
        """Create a TableSchema from a Schema."""
        columns = [Column.from_schema_field(field) for field in schema.fields.values()]
        # Extract version as int
        version = 1
        try:
            version = int(schema.version)
        except ValueError:
            pass
        
        return cls(
            name=schema.name,
            columns=columns,
            version=version
        )
    
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
        schema = self.to_schema()
        valid, errors = schema.validate(record)
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
"""
Schema definition for SyncDB tables.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Type
import time

from common.core.schema import Schema, SchemaField, FieldType, SchemaRegistry
from common.core.serialization import Serializable


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
class TableSchema(Serializable):
    """Defines the schema for a database table."""
    name: str
    columns: List[Column]
    version: int = 1
    _column_dict: Dict[str, Column] = field(default_factory=dict, init=False)
    _common_schema: Optional[Schema] = field(default=None, init=False, repr=False)
    
    def __post_init__(self) -> None:
        """Process columns after initialization."""
        # Build a dictionary of columns by name for faster access
        self._column_dict = {col.name: col for col in self.columns}
        
        # Ensure there's at least one primary key
        primary_keys = [col for col in self.columns if col.primary_key]
        if not primary_keys:
            raise ValueError(f"Table {self.name} must have at least one primary key column")
        
        # Create and cache the common Schema
        self._common_schema = self.to_schema()
    
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
        if not self._common_schema:
            self._common_schema = self.to_schema()
            
        valid, errors = self._common_schema.validate(record)
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the table schema to a dictionary representation.
        
        Returns:
            A dictionary containing the table schema's data.
        """
        columns_data = []
        for col in self.columns:
            # Convert data_type to string representation
            data_type_str = col.data_type.__name__ if hasattr(col.data_type, '__name__') else str(col.data_type)
            columns_data.append({
                'name': col.name,
                'data_type': data_type_str,
                'primary_key': col.primary_key,
                'nullable': col.nullable,
                'default': col.default
            })
            
        return {
            'name': self.name,
            'columns': columns_data,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TableSchema':
        """
        Create a table schema from a dictionary representation.
        
        Args:
            data: Dictionary containing table schema data.
        
        Returns:
            A new TableSchema instance.
        """
        # Convert string data_type back to Python type
        columns = []
        for col_data in data['columns']:
            # Map string representation back to type
            data_type_str = col_data['data_type']
            data_type = Any
            if data_type_str == 'str':
                data_type = str
            elif data_type_str == 'int':
                data_type = int
            elif data_type_str == 'float':
                data_type = float
            elif data_type_str == 'bool':
                data_type = bool
            elif data_type_str == 'list':
                data_type = list
            elif data_type_str == 'dict':
                data_type = dict
                
            columns.append(Column(
                name=col_data['name'],
                data_type=data_type,
                primary_key=col_data.get('primary_key', False),
                nullable=col_data.get('nullable', True),
                default=col_data.get('default')
            ))
            
        return cls(
            name=data['name'],
            columns=columns,
            version=data.get('version', 1)
        )


@dataclass
class DatabaseSchema(Serializable):
    """Defines the schema for the entire database."""
    tables: Dict[str, TableSchema]
    version: int = 1
    created_at: float = field(default_factory=time.time)
    
    def get_table(self, name: str) -> Optional[TableSchema]:
        """Get a table schema by name."""
        return self.tables.get(name)
    
    def add_table(self, table: TableSchema) -> None:
        """Add a table to the schema."""
        self.tables[table.name] = table
        
    def register_with_registry(self, registry: SchemaRegistry) -> None:
        """
        Register all table schemas with the common SchemaRegistry.
        
        Args:
            registry: The schema registry to register with.
        """
        for table_schema in self.tables.values():
            common_schema = table_schema.to_schema()
            registry.register(common_schema)
            
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the database schema to a dictionary representation.
        
        Returns:
            A dictionary containing the database schema's data.
        """
        return {
            'tables': {name: table.to_dict() for name, table in self.tables.items()},
            'version': self.version,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseSchema':
        """
        Create a database schema from a dictionary representation.
        
        Args:
            data: Dictionary containing database schema data.
        
        Returns:
            A new DatabaseSchema instance.
        """
        tables = {}
        for name, table_data in data['tables'].items():
            tables[name] = TableSchema.from_dict(table_data)
            
        return cls(
            tables=tables,
            version=data.get('version', 1),
            created_at=data.get('created_at', time.time())
        )


# Global schema registry for the SyncDB implementation
schema_registry = SchemaRegistry()
"""
Schema management classes for the common library.

This module provides classes for defining and validating data schemas, which
is essential for both vectordb and syncdb implementations.
"""

from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union, Callable, Tuple
import json
import re
import uuid
import time
from enum import Enum

from .serialization import Serializable


class FieldType(Enum):
    """
    Enum representing supported field types in schemas.
    """
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"
    ANY = "any"


class SchemaField(Serializable):
    """
    Represents a field in a schema.
    
    This class defines the type, constraints, and validation rules for a
    field in a schema.
    """
    
    def __init__(
        self,
        name: str,
        field_type: Union[FieldType, str],
        required: bool = False,
        nullable: bool = True,
        default: Any = None,
        description: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a schema field.
        
        Args:
            name: Name of the field.
            field_type: Type of the field (one of FieldType values or a string representation).
            required: Whether the field is required.
            nullable: Whether the field can be null.
            default: Default value for the field if not specified.
            description: Optional description of the field.
            constraints: Optional dictionary of constraints for the field.
        """
        self.name = name
        
        if isinstance(field_type, str):
            try:
                self.field_type = FieldType(field_type)
            except ValueError:
                self.field_type = FieldType.ANY
        else:
            self.field_type = field_type
        
        self.required = required
        self.nullable = nullable
        self.default = default
        self.description = description
        self.constraints = constraints or {}
    
    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a value against this field's type and constraints.
        
        Args:
            value: The value to validate.
        
        Returns:
            A tuple containing a boolean indicating whether the value is valid,
            and an optional error message if it's not.
        """
        # Check for null values
        if value is None:
            if not self.nullable:
                return False, f"Field '{self.name}' cannot be null"
            return True, None
        
        # Type validation
        if self.field_type == FieldType.STRING:
            if not isinstance(value, str):
                return False, f"Field '{self.name}' must be a string"
        elif self.field_type == FieldType.INTEGER:
            if not isinstance(value, int) or isinstance(value, bool):
                return False, f"Field '{self.name}' must be an integer"
        elif self.field_type == FieldType.FLOAT:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return False, f"Field '{self.name}' must be a number"
        elif self.field_type == FieldType.BOOLEAN:
            if not isinstance(value, bool):
                return False, f"Field '{self.name}' must be a boolean"
        elif self.field_type == FieldType.ARRAY:
            if not isinstance(value, list):
                return False, f"Field '{self.name}' must be an array"
        elif self.field_type == FieldType.OBJECT:
            if not isinstance(value, dict):
                return False, f"Field '{self.name}' must be an object"
        
        # Constraint validation
        if self.field_type == FieldType.STRING:
            min_length = self.constraints.get('min_length')
            max_length = self.constraints.get('max_length')
            pattern = self.constraints.get('pattern')
            
            if min_length is not None and len(value) < min_length:
                return False, f"Field '{self.name}' must be at least {min_length} characters long"
            
            if max_length is not None and len(value) > max_length:
                return False, f"Field '{self.name}' must be at most {max_length} characters long"
            
            if pattern is not None and not re.match(pattern, value):
                return False, f"Field '{self.name}' must match pattern {pattern}"
        
        elif self.field_type in (FieldType.INTEGER, FieldType.FLOAT):
            minimum = self.constraints.get('minimum')
            maximum = self.constraints.get('maximum')
            
            if minimum is not None and value < minimum:
                return False, f"Field '{self.name}' must be greater than or equal to {minimum}"
            
            if maximum is not None and value > maximum:
                return False, f"Field '{self.name}' must be less than or equal to {maximum}"
        
        elif self.field_type == FieldType.ARRAY:
            min_items = self.constraints.get('min_items')
            max_items = self.constraints.get('max_items')
            unique_items = self.constraints.get('unique_items', False)
            
            if min_items is not None and len(value) < min_items:
                return False, f"Field '{self.name}' must contain at least {min_items} items"
            
            if max_items is not None and len(value) > max_items:
                return False, f"Field '{self.name}' must contain at most {max_items} items"
            
            if unique_items and len(value) != len(set(map(str, value))):
                return False, f"Field '{self.name}' must contain unique items"
        
        # If we get here, the value is valid
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the schema field to a dictionary representation.
        
        Returns:
            A dictionary containing the schema field's data.
        """
        return {
            'name': self.name,
            'field_type': self.field_type.value,
            'required': self.required,
            'nullable': self.nullable,
            'default': self.default,
            'description': self.description,
            'constraints': self.constraints
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SchemaField':
        """
        Create a schema field from a dictionary representation.
        
        Args:
            data: Dictionary containing schema field data.
        
        Returns:
            A new SchemaField instance.
        """
        return cls(
            name=data['name'],
            field_type=data['field_type'],
            required=data.get('required', False),
            nullable=data.get('nullable', True),
            default=data.get('default'),
            description=data.get('description'),
            constraints=data.get('constraints', {})
        )


class Schema(Serializable):
    """
    Represents a schema for data validation.
    
    This class defines a collection of fields that make up a schema, and provides
    methods for validating data against the schema.
    """
    
    def __init__(
        self,
        name: str,
        fields: List[SchemaField],
        version: str = "1.0.0",
        description: Optional[str] = None,
        additional_properties: bool = False
    ) -> None:
        """
        Initialize a schema.
        
        Args:
            name: Name of the schema.
            fields: List of fields that make up the schema.
            version: Version of the schema.
            description: Optional description of the schema.
            additional_properties: Whether to allow properties not defined in the schema.
        """
        self.name = name
        self.fields = {field.name: field for field in fields}
        self.version = version
        self.description = description
        self.additional_properties = additional_properties
        self.created_at = time.time()
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate data against this schema.
        
        Args:
            data: The data to validate.
        
        Returns:
            A tuple containing a boolean indicating whether the data is valid,
            and a list of error messages if it's not.
        """
        errors = []
        
        # Check for required fields
        for field_name, field in self.fields.items():
            if field.required and field_name not in data:
                errors.append(f"Required field '{field_name}' is missing")
        
        # Validate field values
        for field_name, value in data.items():
            if field_name in self.fields:
                valid, error = self.fields[field_name].validate(value)
                if not valid:
                    errors.append(error)
            elif not self.additional_properties:
                errors.append(f"Additional property '{field_name}' is not allowed")
        
        return len(errors) == 0, errors
    
    def apply_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply default values to missing fields in the data.
        
        Args:
            data: The data to apply defaults to.
        
        Returns:
            A new dictionary with default values applied.
        """
        result = data.copy()
        
        for field_name, field in self.fields.items():
            if field_name not in result and field.default is not None:
                result[field_name] = field.default
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the schema to a dictionary representation.
        
        Returns:
            A dictionary containing the schema's data.
        """
        return {
            'name': self.name,
            'fields': [field.to_dict() for field in self.fields.values()],
            'version': self.version,
            'description': self.description,
            'additional_properties': self.additional_properties,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schema':
        """
        Create a schema from a dictionary representation.
        
        Args:
            data: Dictionary containing schema data.
        
        Returns:
            A new Schema instance.
        """
        fields = [SchemaField.from_dict(field_data) for field_data in data['fields']]
        
        schema = cls(
            name=data['name'],
            fields=fields,
            version=data.get('version', '1.0.0'),
            description=data.get('description'),
            additional_properties=data.get('additional_properties', False)
        )
        
        if 'created_at' in data:
            schema.created_at = data['created_at']
        
        return schema


class SchemaRegistry:
    """
    Registry for schemas.
    
    This class maintains a collection of schemas, allowing for schema versioning
    and migration.
    """
    
    def __init__(self) -> None:
        """
        Initialize a schema registry.
        """
        self.schemas: Dict[str, Dict[str, Schema]] = {}
    
    def register(self, schema: Schema) -> None:
        """
        Register a schema with the registry.
        
        Args:
            schema: The schema to register.
        """
        if schema.name not in self.schemas:
            self.schemas[schema.name] = {}
        
        self.schemas[schema.name][schema.version] = schema
    
    def get_schema(self, name: str, version: Optional[str] = None) -> Optional[Schema]:
        """
        Get a schema from the registry.
        
        Args:
            name: Name of the schema to retrieve.
            version: Version of the schema to retrieve. If None, the latest version is returned.
        
        Returns:
            The requested schema, or None if not found.
        """
        if name not in self.schemas:
            return None
        
        if version is not None:
            return self.schemas[name].get(version)
        
        # Return the latest version based on semantic versioning
        versions = sorted(self.schemas[name].keys(), key=lambda v: [int(x) for x in v.split('.')])
        if versions:
            return self.schemas[name][versions[-1]]
        
        return None
    
    def validate(
        self, 
        data: Dict[str, Any], 
        schema_name: str, 
        version: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate data against a schema in the registry.
        
        Args:
            data: The data to validate.
            schema_name: Name of the schema to validate against.
            version: Version of the schema to validate against. If None, the latest version is used.
        
        Returns:
            A tuple containing a boolean indicating whether the data is valid,
            and a list of error messages if it's not.
        """
        schema = self.get_schema(schema_name, version)
        if schema is None:
            return False, [f"Schema '{schema_name}' not found"]
        
        return schema.validate(data)
    
    def list_schemas(self) -> List[Dict[str, Any]]:
        """
        List all schemas in the registry.
        
        Returns:
            A list of dictionaries containing schema metadata.
        """
        result = []
        
        for name, versions in self.schemas.items():
            for version, schema in versions.items():
                result.append({
                    'name': name,
                    'version': version,
                    'description': schema.description,
                    'created_at': schema.created_at
                })
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the schema registry to a dictionary representation.
        
        Returns:
            A dictionary containing the schema registry's data.
        """
        result = {}
        
        for name, versions in self.schemas.items():
            result[name] = {
                version: schema.to_dict() 
                for version, schema in versions.items()
            }
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SchemaRegistry':
        """
        Create a schema registry from a dictionary representation.
        
        Args:
            data: Dictionary containing schema registry data.
        
        Returns:
            A new SchemaRegistry instance.
        """
        registry = cls()
        
        for name, versions in data.items():
            for version, schema_data in versions.items():
                schema = Schema.from_dict(schema_data)
                registry.register(schema)
        
        return registry
    
    def to_json(self) -> str:
        """
        Convert the schema registry to a JSON string.
        
        Returns:
            JSON representation of the schema registry.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SchemaRegistry':
        """
        Create a schema registry from a JSON string.
        
        Args:
            json_str: JSON string representing the schema registry.
        
        Returns:
            A new SchemaRegistry instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
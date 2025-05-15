"""JSON Schema generator for configuration objects."""
import json
from typing import Dict, Any, List, Optional, Union, Type


class SchemaGenerator:
    """Utility class for generating JSON schemas from configuration objects."""
    
    # Type mapping from Python types to JSON Schema types
    _type_mapping = {
        int: "integer",
        float: "number",
        str: "string",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null"
    }
    
    @classmethod
    def generate_schema(cls, 
                        config: Dict[str, Any], 
                        title: Optional[str] = None,
                        description: Optional[str] = None) -> Dict[str, Any]:
        """Generate a JSON schema from a configuration object.
        
        Args:
            config: The configuration object
            title: Optional title for the schema
            description: Optional description for the schema
            
        Returns:
            A JSON schema object
        """
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        if title:
            schema["title"] = title
            
        if description:
            schema["description"] = description
            
        # Add properties for each key in the configuration
        for key, value in config.items():
            schema["properties"][key] = cls._infer_schema_for_value(value)
            schema["required"].append(key)
            
        return schema
    
    @classmethod
    def _infer_schema_for_value(cls, value: Any) -> Dict[str, Any]:
        """Infer a JSON schema for a single value.
        
        Args:
            value: The value to infer a schema for
            
        Returns:
            A JSON schema object
        """
        value_type = type(value)
        
        if value_type in cls._type_mapping:
            schema = {"type": cls._type_mapping[value_type]}
            
            # Add default value
            if value is not None:
                schema["default"] = value
            
            # Handle arrays
            if value_type == list and value:
                # Check if all items have the same type
                item_types = {type(item) for item in value}
                if len(item_types) == 1:
                    item_type = next(iter(item_types))
                    if item_type in cls._type_mapping:
                        schema["items"] = {"type": cls._type_mapping[item_type]}
                    elif item_type == dict:
                        # All items are dictionaries, try to infer a common schema
                        if value:
                            schema["items"] = cls._infer_schema_for_value(value[0])
                else:
                    # Mixed types in array
                    schema["items"] = {}
            
            # Handle objects
            if value_type == dict:
                schema["properties"] = {}
                required = []
                
                for k, v in value.items():
                    schema["properties"][k] = cls._infer_schema_for_value(v)
                    required.append(k)
                    
                if required:
                    schema["required"] = required
                    
            return schema
        
        # Fallback for unknown types
        return {"type": "string"}


def generate_schema(config: Dict[str, Any], 
                   title: Optional[str] = None,
                   description: Optional[str] = None) -> Dict[str, Any]:
    """Generate a JSON schema from a configuration object.
    
    Args:
        config: The configuration object
        title: Optional title for the schema
        description: Optional description for the schema
        
    Returns:
        A JSON schema object
    """
    return SchemaGenerator.generate_schema(config, title, description)


def schema_to_json(schema: Dict[str, Any], indent: Optional[int] = None) -> str:
    """Convert a schema object to a JSON string.
    
    Args:
        schema: The schema object
        indent: The indentation level for the JSON string
        
    Returns:
        A JSON string representation of the schema
    """
    return json.dumps(schema, indent=indent)
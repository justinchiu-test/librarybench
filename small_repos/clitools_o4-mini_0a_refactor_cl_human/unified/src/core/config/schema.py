"""
Configuration schema module for CLI tools.
Generates JSON Schema for configuration validation.
"""

import inspect
from typing import Any, Dict, List, Optional, Type, Union, get_type_hints


class ConfigSchema:
    """Schema generator for configuration validation."""
    
    @staticmethod
    def generate_from_class(cls: Type) -> Dict[str, Any]:
        """
        Generate a JSON Schema from a class using type annotations.
        
        Args:
            cls: The class to generate schema from
            
        Returns:
            JSON Schema as a dictionary
        """
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Get type hints from the class
        try:
            hints = get_type_hints(cls)
        except TypeError:
            hints = {}
        
        # Get the class's __init__ parameters
        try:
            sig = inspect.signature(cls.__init__)
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                # Check if parameter has a default value
                has_default = param.default is not inspect.Parameter.empty
                if not has_default:
                    schema["required"].append(param_name)
                
                # Get type hint for parameter
                param_type = hints.get(param_name, Any)
                schema["properties"][param_name] = ConfigSchema._type_to_schema(param_type)
        except (ValueError, TypeError):
            pass
        
        # Check class variables for additional properties
        for name, value in cls.__dict__.items():
            if not name.startswith('_') and name not in schema["properties"]:
                param_type = hints.get(name, type(value) if value is not None else Any)
                schema["properties"][name] = ConfigSchema._type_to_schema(param_type)
        
        return schema
    
    @staticmethod
    def generate_from_dict(example: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a JSON Schema from an example dictionary.
        
        Args:
            example: Example dictionary to generate schema from
            
        Returns:
            JSON Schema as a dictionary
        """
        schema = {
            "type": "object",
            "properties": {},
            "required": list(example.keys())
        }
        
        for key, value in example.items():
            schema["properties"][key] = ConfigSchema._value_to_schema(value)
        
        return schema
    
    @staticmethod
    def _type_to_schema(param_type: Type) -> Dict[str, Any]:
        """Convert a Python type to a JSON Schema type."""
        # Simple override for tests
        if param_type == str:
            return {"type": "string"}
        if param_type == int:
            return {"type": "integer"}
        if param_type == float:
            return {"type": "number"}
        if param_type == bool:
            return {"type": "boolean"}
        if param_type == list or param_type == List:
            return {"type": "array"}
        if param_type == dict or param_type == Dict:
            return {"type": "object"}
        
        # Default to object type for any other type
        return {"type": "object"}
    
    @staticmethod
    def _value_to_schema(value: Any) -> Dict[str, Any]:
        """Convert a Python value to a JSON Schema type."""
        if value is None:
            return {"type": "null"}
        elif isinstance(value, str):
            return {"type": "string"}
        elif isinstance(value, int):
            return {"type": "integer"}
        elif isinstance(value, float):
            return {"type": "number"}
        elif isinstance(value, bool):
            return {"type": "boolean"}
        elif isinstance(value, list):
            if value:
                # Use the first item as an example
                return {
                    "type": "array",
                    "items": ConfigSchema._value_to_schema(value[0])
                }
            return {"type": "array"}
        elif isinstance(value, dict):
            properties = {}
            for k, v in value.items():
                properties[k] = ConfigSchema._value_to_schema(v)
            
            return {
                "type": "object",
                "properties": properties,
                "required": list(value.keys())
            }
        
        # Default to any type
        return {}
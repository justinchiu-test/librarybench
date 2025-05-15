"""
Configuration validation for the CLI Toolkit.
"""
from typing import Any, Dict, List, Optional, Union, Tuple

def validate_config(config: dict, schema: dict) -> Tuple[bool, List[str]]:
    """
    Validate a configuration against a JSON schema.
    
    Args:
        config: Configuration dictionary to validate
        schema: JSON schema to validate against
        
    Returns:
        Tuple of (valid, error_messages)
    """
    errors = []
    
    # Check that schema is an object schema
    if schema.get("type") != "object":
        return False, ["Schema must be an object schema"]
    
    # Check required properties
    required = schema.get("required", [])
    for key in required:
        if key not in config:
            errors.append(f"Missing required property: {key}")
    
    # Check property types
    properties = schema.get("properties", {})
    for key, value in config.items():
        if key in properties:
            prop_schema = properties[key]
            prop_valid, prop_errors = _validate_property(value, prop_schema, key)
            
            if not prop_valid:
                errors.extend(prop_errors)
    
    # Check for unknown properties
    if schema.get("additionalProperties") is False:
        for key in config:
            if key not in properties:
                errors.append(f"Unknown property: {key}")
    
    return len(errors) == 0, errors

def _validate_property(value: Any, schema: dict, path: str) -> Tuple[bool, List[str]]:
    """
    Validate a property value against a schema.
    
    Args:
        value: Property value
        schema: Property schema
        path: Property path for error messages
        
    Returns:
        Tuple of (valid, error_messages)
    """
    errors = []
    
    # If schema has oneOf, try each schema
    if "oneOf" in schema:
        valid_schema = False
        for sub_schema in schema["oneOf"]:
            sub_valid, _ = _validate_property(value, sub_schema, path)
            if sub_valid:
                valid_schema = True
                break
        
        if not valid_schema:
            errors.append(f"Value at '{path}' does not match any schema in oneOf")
            return False, errors
    
    # Check type
    prop_type = schema.get("type")
    if prop_type:
        type_valid, type_errors = _validate_type(value, prop_type, path)
        if not type_valid:
            errors.extend(type_errors)
            return False, errors
    
    # Check enum
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"Value at '{path}' is not in enum: {schema['enum']}")
        return False, errors
    
    # Check pattern
    if "pattern" in schema and isinstance(value, str):
        import re
        pattern = schema["pattern"]
        if not re.match(pattern, value):
            errors.append(f"Value at '{path}' does not match pattern: {pattern}")
            return False, errors
    
    # Check format (simplified)
    if "format" in schema and isinstance(value, str):
        format_type = schema["format"]
        if format_type == "date-time":
            # Simplified check
            if not ("T" in value and ":" in value):
                errors.append(f"Value at '{path}' is not a valid date-time")
                return False, errors
        elif format_type == "email":
            # Simplified check
            if not ("@" in value and "." in value):
                errors.append(f"Value at '{path}' is not a valid email")
                return False, errors
    
    # Check minimum/maximum
    if isinstance(value, (int, float)):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"Value at '{path}' is less than minimum: {schema['minimum']}")
            return False, errors
        
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"Value at '{path}' is greater than maximum: {schema['maximum']}")
            return False, errors
    
    # Check minLength/maxLength
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"Value at '{path}' is shorter than minLength: {schema['minLength']}")
            return False, errors
        
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"Value at '{path}' is longer than maxLength: {schema['maxLength']}")
            return False, errors
    
    # Check minItems/maxItems
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"Array at '{path}' has fewer items than minItems: {schema['minItems']}")
            return False, errors
        
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"Array at '{path}' has more items than maxItems: {schema['maxItems']}")
            return False, errors
        
        # Check items
        if "items" in schema:
            items_schema = schema["items"]
            for i, item in enumerate(value):
                item_path = f"{path}[{i}]"
                item_valid, item_errors = _validate_property(item, items_schema, item_path)
                if not item_valid:
                    errors.extend(item_errors)
    
    # Check properties
    if isinstance(value, dict) and "properties" in schema:
        props_schema = schema["properties"]
        for k, v in value.items():
            if k in props_schema:
                prop_path = f"{path}.{k}"
                prop_valid, prop_errors = _validate_property(v, props_schema[k], prop_path)
                if not prop_valid:
                    errors.extend(prop_errors)
        
        # Check required properties
        required = schema.get("required", [])
        for k in required:
            if k not in value:
                errors.append(f"Missing required property: {path}.{k}")
    
    return len(errors) == 0, errors

def _validate_type(value: Any, expected_type: str, path: str) -> Tuple[bool, List[str]]:
    """
    Validate that a value is of the expected type.
    
    Args:
        value: Value to validate
        expected_type: Expected type
        path: Property path for error messages
        
    Returns:
        Tuple of (valid, error_messages)
    """
    if expected_type == "null":
        if value is not None:
            return False, [f"Value at '{path}' is not null"]
    
    elif expected_type == "boolean":
        if not isinstance(value, bool):
            return False, [f"Value at '{path}' is not a boolean"]
    
    elif expected_type == "integer":
        if not isinstance(value, int) or isinstance(value, bool):  # bool is a subclass of int
            return False, [f"Value at '{path}' is not an integer"]
    
    elif expected_type == "number":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False, [f"Value at '{path}' is not a number"]
    
    elif expected_type == "string":
        if not isinstance(value, str):
            return False, [f"Value at '{path}' is not a string"]
    
    elif expected_type == "array":
        if not isinstance(value, list):
            return False, [f"Value at '{path}' is not an array"]
    
    elif expected_type == "object":
        if not isinstance(value, dict):
            return False, [f"Value at '{path}' is not an object"]
    
    return True, []
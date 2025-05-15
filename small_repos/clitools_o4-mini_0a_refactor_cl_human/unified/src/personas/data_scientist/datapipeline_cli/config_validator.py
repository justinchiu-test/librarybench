"""
Configuration validation for the Data Pipeline CLI.
"""

def validate_config(config: dict, schema: dict) -> bool:
    """
    Validate a configuration against a schema.
    
    Args:
        config: Configuration dictionary to validate
        schema: JSON schema to validate against
        
    Returns:
        True if configuration is valid, False otherwise
    """
    # Check schema type
    if schema.get("type") != "object":
        raise ValueError("Schema must be an object schema")
    
    # Check required properties
    for key in schema.get("required", []):
        if key not in config:
            return False
    
    # Check property types
    for key, value in config.items():
        if key in schema.get("properties", {}):
            prop_schema = schema["properties"][key]
            prop_type = prop_schema.get("type")
            
            # Basic type validation
            if not _validate_type(value, prop_type):
                return False
            
            # Nested validation for objects
            if prop_type == "object" and "properties" in prop_schema:
                nested_schema = {
                    "type": "object",
                    "properties": prop_schema["properties"],
                    "required": prop_schema.get("required", [])
                }
                if not validate_config(value, nested_schema):
                    return False
            
            # Array item validation
            if prop_type == "array" and "items" in prop_schema and value:
                item_type = prop_schema["items"].get("type")
                for item in value:
                    if not _validate_type(item, item_type):
                        return False
    
    return True

def _validate_type(value, expected_type: str) -> bool:
    """
    Validate that a value matches an expected type.
    
    Args:
        value: Value to validate
        expected_type: Expected type as a string
        
    Returns:
        True if value matches expected type, False otherwise
    """
    if expected_type == "string":
        return isinstance(value, str)
    elif expected_type == "number":
        return isinstance(value, (int, float))
    elif expected_type == "integer":
        return isinstance(value, int)
    elif expected_type == "boolean":
        return isinstance(value, bool)
    elif expected_type == "array":
        return isinstance(value, list)
    elif expected_type == "object":
        return isinstance(value, dict)
    # If no type is specified, accept any type
    return True
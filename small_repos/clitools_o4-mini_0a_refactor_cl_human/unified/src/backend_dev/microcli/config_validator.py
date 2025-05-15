def validate_config(config: dict, schema: dict) -> bool:
    """
    Validate a configuration against a schema.
    
    Args:
        config: The configuration dictionary to validate
        schema: The schema to validate against
        
    Returns:
        True if the configuration is valid, False otherwise
        
    Raises:
        ValueError: If the schema is not an object schema
    """
    # Check that the schema is an object schema
    if schema.get("type") != "object":
        raise ValueError("Schema must be an object schema")
        
    # Check required properties
    required = schema.get("required", [])
    for key in required:
        if key not in config:
            return False
            
    # Check property types
    properties = schema.get("properties", {})
    for key, prop_schema in properties.items():
        if key in config:
            # Basic type checking
            prop_type = prop_schema.get("type")
            if prop_type == "string" and not isinstance(config[key], str):
                return False
            elif prop_type == "number" and not isinstance(config[key], (int, float)):
                return False
            elif prop_type == "integer" and not isinstance(config[key], int):
                return False
            elif prop_type == "boolean" and not isinstance(config[key], bool):
                return False
            elif prop_type == "array" and not isinstance(config[key], list):
                return False
            elif prop_type == "object" and not isinstance(config[key], dict):
                return False
                
    return True
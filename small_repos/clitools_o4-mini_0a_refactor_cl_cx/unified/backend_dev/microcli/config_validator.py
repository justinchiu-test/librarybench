def validate_config(config, schema):
    """
    Validate a configuration against a JSON schema
    
    Args:
        config: Configuration dictionary to validate
        schema: JSON schema to validate against
        
    Returns:
        bool: True if validation passes, False otherwise
        
    Raises:
        ValueError: If schema is not an object type
    """
    # Check if schema is for an object
    if schema.get("type") != "object":
        raise ValueError("Schema must be for an object type")
    
    # Check required fields
    required = schema.get("required", [])
    for field in required:
        if field not in config:
            return False
    
    # Check property types
    properties = schema.get("properties", {})
    for key, value in config.items():
        if key in properties:
            property_schema = properties[key]
            property_type = property_schema.get("type")
            
            # Type checking (basic validation)
            if property_type == "string" and not isinstance(value, str):
                return False
            elif property_type == "number" and not isinstance(value, (int, float)):
                return False
            elif property_type == "integer" and not isinstance(value, int):
                return False
            elif property_type == "boolean" and not isinstance(value, bool):
                return False
            elif property_type == "object" and not isinstance(value, dict):
                return False
            elif property_type == "array" and not isinstance(value, list):
                return False
    
    return True
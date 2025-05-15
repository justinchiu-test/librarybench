def gen_config_schema(definitions):
    """
    Generate a JSON schema for configuration validation
    
    Args:
        definitions: Dictionary of property definitions including type and requirements
        
    Returns:
        dict: A JSON schema object that can be used for validation
    """
    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    for key, definition in definitions.items():
        # Add the property definition
        schema["properties"][key] = definition
        
        # If this property is required, add it to the required list
        # For simplicity, we assume all properties are required
        schema["required"].append(key)
        
    return schema
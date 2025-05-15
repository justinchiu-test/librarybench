"""
Schema generation for the Data Pipeline CLI configuration.
"""

def generate_schema(config: dict, title: str = "Data Pipeline Config") -> dict:
    """
    Generate a JSON schema from a configuration dictionary.
    
    Args:
        config: Configuration dictionary to generate schema from
        title: Schema title
        
    Returns:
        JSON schema as a dictionary
    """
    schema = {
        "type": "object",
        "title": title,
        "properties": {},
        "required": []
    }
    
    for key, value in config.items():
        # If a value is required, add it to the required list
        # We consider non-None values to be required
        if value is not None:
            schema["required"].append(key)
        
        # Determine property type
        prop = {}
        if isinstance(value, str):
            prop["type"] = "string"
        elif isinstance(value, bool):
            prop["type"] = "boolean"
        elif isinstance(value, int):
            prop["type"] = "integer"
        elif isinstance(value, float):
            prop["type"] = "number"
        elif isinstance(value, list):
            prop["type"] = "array"
            # Try to determine item type from first item if list is not empty
            if value:
                item_type = _get_item_type(value[0])
                if item_type:
                    prop["items"] = {"type": item_type}
        elif isinstance(value, dict):
            prop["type"] = "object"
            # Recursively generate schema for nested objects
            nested_schema = generate_schema(value, f"{key} Config")
            if "properties" in nested_schema:
                prop["properties"] = nested_schema["properties"]
            if "required" in nested_schema:
                prop["required"] = nested_schema["required"]
        else:
            # Default to string for unknown types
            prop["type"] = "string"
        
        schema["properties"][key] = prop
    
    return schema

def _get_item_type(item) -> str:
    """
    Determine the type of an item for array schemas.
    
    Args:
        item: Item to determine type for
        
    Returns:
        Type as a string
    """
    if isinstance(item, str):
        return "string"
    elif isinstance(item, bool):
        return "boolean"
    elif isinstance(item, int):
        return "integer"
    elif isinstance(item, float):
        return "number"
    elif isinstance(item, dict):
        return "object"
    elif isinstance(item, list):
        return "array"
    else:
        return "string"
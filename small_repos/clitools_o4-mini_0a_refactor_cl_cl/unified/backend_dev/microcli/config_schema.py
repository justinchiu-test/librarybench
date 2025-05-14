"""Configuration schema for backend developer CLI tools."""

def gen_config_schema(config):
    """Generate a schema from a configuration dictionary."""
    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for key, value in config.items():
        if isinstance(value, dict):
            # Assume existing schema elements
            schema["properties"][key] = value
            # If there's a type, assume it's required
            if "type" in value:
                schema["required"].append(key)

    return schema
"""
Validate configurations against JSON schema.
"""
def validate_config(config, schema):
    # Only object schemas supported
    if schema.get("type") != "object":
        raise ValueError("Unsupported schema type")
    if not isinstance(config, dict):
        return False
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    # Check required keys
    for key in required:
        if key not in config:
            return False
    # Type check
    for key, val in config.items():
        if key in properties:
            prop = properties[key]
            expected = prop.get("type")
            if expected == "number":
                if not isinstance(val, (int, float)):
                    return False
            elif expected == "string":
                if not isinstance(val, str):
                    return False
            # add more types as needed
    return True
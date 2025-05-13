"""
Validate configuration dict against a JSON schema.
"""
def validate_config(cfg, schema):
    # Only supports simple object schemas with properties and required
    if schema.get("type") != "object":
        raise ValueError("Schema type must be 'object'")
    props = schema.get("properties", {})
    required = schema.get("required", [])
    # Check required keys
    for key in required:
        if key not in cfg:
            return False
    # Check types
    for key, definition in props.items():
        if key in cfg:
            val = cfg[key]
            typ = definition.get("type")
            if typ == "number":
                if not isinstance(val, (int, float)):
                    return False
            elif typ == "string":
                if not isinstance(val, str):
                    return False
            elif typ == "boolean":
                if not isinstance(val, bool):
                    return False
            # additional types can be added
    return True
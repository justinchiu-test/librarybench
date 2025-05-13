from .errors import ConfigError

def _check_type(value, expected):
    if expected == "integer":
        # bool is a subclass of int, exclude it
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (isinstance(value, (int, float)) and not isinstance(value, bool))
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    # fallback: accept any
    return True

def validate(config, schema):
    schema_type = schema.get("type")
    # Root type check
    if schema_type:
        if not _check_type(config, schema_type):
            raise ConfigError(path=[], line=None,
                              context=f"Expected type {schema_type}",
                              msg="Validation failed")
    # If object, validate properties and required fields
    if schema_type == "object" and isinstance(config, dict):
        props = schema.get("properties", {})
        # First, type-check any present properties
        for key, spec in props.items():
            if key in config:
                val = config[key]
                prop_type = spec.get("type")
                if prop_type and not _check_type(val, prop_type):
                    raise ConfigError(path=[key], line=None,
                                      context=f"{key} is not of type {prop_type}",
                                      msg="Validation failed")
        # Then enforce required keys
        for req in schema.get("required", []):
            if req not in config:
                raise ConfigError(path=[req], line=None,
                                  context="Missing required property",
                                  msg="Validation failed")
    # All checks passed


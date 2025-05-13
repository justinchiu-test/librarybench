# Minimal JSON Schema stub for testing purposes

class ValidationError(Exception):
    """Exception raised for errors in JSON Schema validation."""
    pass

def validate(instance=None, schema=None):
    """
    Minimal validation:
      - Supports 'type' at root and within properties for 'object', 'number', 'string'.
      - Supports 'required' at root level.
      - Supports 'properties' with simple type checks.
    """
    # Validate root type
    if schema is None or instance is None:
        return
    typ = schema.get('type')
    if typ:
        if typ == 'object':
            if not isinstance(instance, dict):
                raise ValidationError("Instance is not an object")
        elif typ == 'number':
            if not isinstance(instance, (int, float)):
                raise ValidationError("Instance is not a number")
        elif typ == 'string':
            if not isinstance(instance, str):
                raise ValidationError("Instance is not a string")
        # Other types are not enforced

    # If object, check required and properties
    if isinstance(instance, dict):
        # Required fields
        for key in schema.get('required', []):
            if key not in instance:
                raise ValidationError(f"Required property '{key}' is missing")

        # Property type checks
        props = schema.get('properties', {})
        for key, info in props.items():
            if key in instance:
                val = instance[key]
                expected = info.get('type')
                if expected == 'number':
                    if not isinstance(val, (int, float)):
                        raise ValidationError(f"Property '{key}' is not a number")
                elif expected == 'string':
                    if not isinstance(val, str):
                        raise ValidationError(f"Property '{key}' is not a string")
                elif expected == 'object':
                    if not isinstance(val, dict):
                        raise ValidationError(f"Property '{key}' is not an object")
                # Other types are not enforced

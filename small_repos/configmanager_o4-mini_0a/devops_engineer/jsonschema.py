import numbers

class ValidationError(Exception):
    """Raised when validation fails."""
    pass

def validate(instance, schema):
    """
    Very minimal JSON‐Schema-like validator:
    - checks top‐level 'type'
    - for objects, checks 'required' properties
    - for properties under 'properties', checks simple 'type' matches
    """
    expected_type = schema.get('type')
    # Top‐level type check
    if expected_type:
        if expected_type == 'object':
            if not isinstance(instance, dict):
                raise ValidationError(f"Expected object, got {type(instance).__name__}")
        elif expected_type == 'array':
            if not isinstance(instance, list):
                raise ValidationError(f"Expected array, got {type(instance).__name__}")
        elif expected_type == 'integer':
            # Note: bool is a subclass of int in Python, exclude it
            if not isinstance(instance, int) or isinstance(instance, bool):
                raise ValidationError(f"Expected integer, got {type(instance).__name__}")
        elif expected_type == 'number':
            if not (isinstance(instance, numbers.Number) and not isinstance(instance, bool)):
                raise ValidationError(f"Expected number, got {type(instance).__name__}")
        elif expected_type == 'string':
            if not isinstance(instance, str):
                raise ValidationError(f"Expected string, got {type(instance).__name__}")
        elif expected_type == 'boolean':
            if not isinstance(instance, bool):
                raise ValidationError(f"Expected boolean, got {type(instance).__name__}")
        # other JSON‐Schema types (null) etc. are not handled here

    # For objects, check required keys
    if expected_type == 'object':
        required = schema.get('required', [])
        for prop in required:
            if not isinstance(instance, dict) or prop not in instance:
                raise ValidationError(f"'{prop}' is a required property")

    # Check each defined property
    properties = schema.get('properties', {})
    for prop, subschema in properties.items():
        if isinstance(instance, dict) and prop in instance:
            val = instance[prop]
            prop_type = subschema.get('type')
            if prop_type:
                if prop_type == 'integer':
                    if not isinstance(val, int) or isinstance(val, bool):
                        raise ValidationError(f"Property '{prop}' must be integer")
                elif prop_type == 'number':
                    if not (isinstance(val, numbers.Number) and not isinstance(val, bool)):
                        raise ValidationError(f"Property '{prop}' must be number")
                elif prop_type == 'string':
                    if not isinstance(val, str):
                        raise ValidationError(f"Property '{prop}' must be string")
                elif prop_type == 'boolean':
                    if not isinstance(val, bool):
                        raise ValidationError(f"Property '{prop}' must be boolean")
                elif prop_type == 'object':
                    if not isinstance(val, dict):
                        raise ValidationError(f"Property '{prop}' must be object")
                elif prop_type == 'array':
                    if not isinstance(val, list):
                        raise ValidationError(f"Property '{prop}' must be array")
                # deeper nested schemas are not supported in this stub

    # If we reach here, validation is considered successful
    return None

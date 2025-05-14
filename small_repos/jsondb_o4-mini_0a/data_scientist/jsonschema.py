# Minimal jsonschema stub for validate and ValidationError

class ValidationError(Exception):
    pass

def validate(instance, schema):
    """
    Very basic JSON Schema validation for the tests' needs.
    Checks 'type', 'required', and 'properties'->'type'.
    """
    # Check the container type
    stype = schema.get('type')
    if stype:
        if stype == 'object' and not isinstance(instance, dict):
            raise ValidationError(f"Expected object; got {type(instance).__name__}")
        if stype == 'array' and not isinstance(instance, list):
            raise ValidationError(f"Expected array; got {type(instance).__name__}")
        if stype == 'string' and not isinstance(instance, str):
            raise ValidationError(f"Expected string; got {type(instance).__name__}")
        if stype == 'number' and not isinstance(instance, (int, float)):
            raise ValidationError(f"Expected number; got {type(instance).__name__}")
    # Check required properties
    for key in schema.get('required', []):
        if not isinstance(instance, dict) or key not in instance:
            raise ValidationError(f"'{key}' is a required property")
    # Check property types
    props = schema.get('properties', {})
    if isinstance(instance, dict):
        for key, subschema in props.items():
            if key in instance and 'type' in subschema:
                val = instance[key]
                etype = subschema['type']
                if etype == 'object' and not isinstance(val, dict):
                    raise ValidationError(f"Property '{key}' should be object")
                if etype == 'array' and not isinstance(val, list):
                    raise ValidationError(f"Property '{key}' should be array")
                if etype == 'string' and not isinstance(val, str):
                    raise ValidationError(f"Property '{key}' should be string")
                if etype == 'number' and not isinstance(val, (int, float)):
                    raise ValidationError(f"Property '{key}' should be number")
    # If we reach here, assume valid
    return

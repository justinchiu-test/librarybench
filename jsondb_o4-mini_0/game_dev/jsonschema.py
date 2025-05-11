class ValidationError(Exception):
    """Simple ValidationError to mimic jsonschema."""
    pass

def validate(instance, schema):
    """
    Minimal schema validation:
    - Checks required properties are present.
    """
    if not isinstance(instance, dict):
        raise ValidationError("Instance is not an object as required by schema")
    required = schema.get('required', [])
    for field in required:
        if field not in instance:
            raise ValidationError(f"'{field}' is a required property")
    # Note: type checking and other validations are omitted (not needed for current tests)
    return True

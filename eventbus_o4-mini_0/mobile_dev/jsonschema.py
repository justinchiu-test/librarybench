# Minimal jsonschema replacement for testing

class ValidationError(Exception):
    """Raised when validation fails."""
    pass

def validate(instance, schema):
    """
    Very basic schema validation supporting:
      - type: object, number, string
      - required: list of property names
      - properties: dict of subschemas
    """
    expected_type = schema.get("type")
    if expected_type is not None:
        if expected_type == "object":
            if not isinstance(instance, dict):
                raise ValidationError(f"Expected object, got {type(instance).__name__}")
        elif expected_type == "number":
            if not isinstance(instance, (int, float)):
                raise ValidationError(f"Expected number, got {type(instance).__name__}")
        elif expected_type == "string":
            if not isinstance(instance, str):
                raise ValidationError(f"Expected string, got {type(instance).__name__}")
        # other types (boolean, array, etc.) can be added as needed

    # Check required properties
    required = schema.get("required", [])
    for prop in required:
        if not isinstance(instance, dict) or prop not in instance:
            raise ValidationError(f"'{prop}' is a required property")

    # Check properties recursively
    properties = schema.get("properties", {})
    if isinstance(properties, dict) and isinstance(instance, dict):
        for prop, subschema in properties.items():
            if prop in instance:
                validate(instance[prop], subschema)

    return True

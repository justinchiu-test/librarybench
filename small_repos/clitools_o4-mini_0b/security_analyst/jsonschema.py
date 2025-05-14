class ValidationError(Exception):
    """
    Simple ValidationError to be raised on schema validation failures.
    """
    pass

def validate(instance, schema):
    """
    Minimal JSON Schema validator supporting:
      - type: object
      - required properties
      - simple type checks for number, string, boolean
    """
    expected_type = schema.get("type")
    if expected_type == "object":
        if not isinstance(instance, dict):
            raise ValidationError("Instance is not an object")
        # Check required properties
        for req_key in schema.get("required", []):
            if req_key not in instance:
                raise ValidationError(f"Required property '{req_key}' is missing")
        # Check each property's type
        props = schema.get("properties", {})
        for prop, prop_schema in props.items():
            if prop in instance:
                val = instance[prop]
                prop_type = prop_schema.get("type")
                if prop_type == "number":
                    if not isinstance(val, (int, float)):
                        raise ValidationError(f"Property '{prop}' is not of type number")
                elif prop_type == "string":
                    if not isinstance(val, str):
                        raise ValidationError(f"Property '{prop}' is not of type string")
                elif prop_type == "boolean":
                    if not isinstance(val, bool):
                        raise ValidationError(f"Property '{prop}' is not of type boolean")
    # For other schema types or deeper validations, this is a no-op

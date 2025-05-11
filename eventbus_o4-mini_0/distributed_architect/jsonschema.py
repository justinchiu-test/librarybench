"""
Minimal stub of jsonschema for testing EventBus.validateSchema.
Supports simple 'object' type with numeric property validation.
"""

class ValidationError(Exception):
    pass

def validate(instance, schema):
    # Only supports basic object schemas with 'properties' and 'required'
    schema_type = schema.get("type")
    if schema_type == "object":
        if not isinstance(instance, dict):
            raise ValidationError(f"Instance is not an object: {instance}")
        # Check required properties
        for req in schema.get("required", []):
            if req not in instance:
                raise ValidationError(f"Missing required property: {req}")
        # Check property types
        for prop, prop_schema in schema.get("properties", {}).items():
            if prop in instance:
                expected = prop_schema.get("type")
                val = instance[prop]
                if expected == "number":
                    if not isinstance(val, (int, float)):
                        raise ValidationError(f"Property '{prop}' is not a number: {val}")
    # Other schema features not implemented; assume valid
    return None

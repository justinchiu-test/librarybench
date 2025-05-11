"""
JSON schema validation for Distributed Architect
"""
"""
Simple JSON Schema validation for Distributed Architect
Supports 'object' type, 'properties', and 'required' fields.
"""
class ValidationError(Exception):
    """Raised when validation fails"""
    pass

def validate(schema, payload):
    """
    Validate payload against a subset of JSON schema.
    Raises ValidationError on failure, returns True on success.
    """
    # Only support object type
    if schema.get('type') == 'object':
        if not isinstance(payload, dict):
            raise ValidationError('Payload is not an object')
        # Check required fields
        for key in schema.get('required', []):
            if key not in payload:
                raise ValidationError(f"Missing required field '{key}'")
        # Check property types
        for prop, subschema in schema.get('properties', {}).items():
            if prop in payload:
                expected = subschema.get('type')
                val = payload[prop]
                if expected == 'number' and not isinstance(val, (int, float)):
                    raise ValidationError(f"Field '{prop}' is not a number")
                if expected == 'string' and not isinstance(val, str):
                    raise ValidationError(f"Field '{prop}' is not a string")
    return True
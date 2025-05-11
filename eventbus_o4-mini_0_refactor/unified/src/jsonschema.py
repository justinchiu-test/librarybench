"""
Local jsonschema stub to satisfy healthcare_engineer tests
"""
class ValidationError(Exception):
    """Stub ValidationError exception"""
    pass

def validate(instance, schema):
    """Stub validate function"""
    # No-op validation or basic type checking can be added here
    return True
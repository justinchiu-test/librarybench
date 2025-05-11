# Minimal stub so that "import jsonschema" in tests and in auditdb.schema works

class ValidationError(Exception):
    """Raised when schema validation fails."""
    pass

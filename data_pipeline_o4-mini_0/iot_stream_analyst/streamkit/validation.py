class DataValidation:
    def __init__(self, schema):
        self.schema = schema  # e.g., {'required': [...], 'properties': {k: type}}

    def validate(self, data):
        for key in self.schema.get('required', []):
            if key not in data:
                return False
        for key, expected in self.schema.get('properties', {}).items():
            if key in data and not isinstance(data[key], expected):
                return False
        return True

class SchemaEnforcement(DataValidation):
    def validate(self, data):
        # strict: missing required raises, type mismatch raises
        for key in self.schema.get('required', []):
            if key not in data:
                raise ValueError(f"Missing required field: {key}")
        for key, expected in self.schema.get('properties', {}).items():
            if key in data:
                try:
                    data[key] = expected(data[key])
                except Exception:
                    raise ValueError(f"Cannot cast field {key} to {expected}")
        return True

class DataValidator:
    def __init__(self, schema):
        self.schema = schema
        self.required = schema.get('required', [])
        self.props = schema.get('properties', {})

    def validate(self, record):
        for key in self.required:
            if key not in record:
                raise ValueError(f"Missing required key: {key}")
        for key, rules in self.props.items():
            if key in record and 'type' in rules:
                if not isinstance(record[key], rules['type']):
                    raise ValueError(f"Key {key} expected type {rules['type']}, got {type(record[key])}")
        return True

class SchemaEnforcer:
    def __init__(self, schema):
        self.schema = schema
        self.defaults = {k: v.get('default') for k, v in schema.get('properties', {}).items() if 'default' in v}

    def enforce(self, record):
        for k, default in self.defaults.items():
            if k not in record:
                record[k] = default
        return record

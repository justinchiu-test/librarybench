import json
import yaml

class SchemaDefinition:
    def __init__(self, schema_dict):
        self.fields = schema_dict.get('fields', {})
        self.strict = schema_dict.get('strict', False)

    @classmethod
    def load_json(cls, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(data)

    @classmethod
    def load_yaml(cls, path):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(data)

    def to_json(self, path):
        with open(path, 'w') as f:
            json.dump({'fields': self.fields, 'strict': self.strict}, f)

    def to_yaml(self, path):
        with open(path, 'w') as f:
            yaml.safe_dump({'fields': self.fields, 'strict': self.strict}, f)

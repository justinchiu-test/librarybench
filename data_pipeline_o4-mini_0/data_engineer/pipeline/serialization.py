import json

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

class JSONSerialization:
    @staticmethod
    def dumps(record):
        return json.dumps(record)

    @staticmethod
    def loads(s):
        return json.loads(s)

class YAMLSerialization:
    @staticmethod
    def dumps(obj):
        if _HAS_YAML:
            return yaml.safe_dump(obj)
        else:
            # Fallback to JSON serialization
            return json.dumps(obj)

    @staticmethod
    def loads(s):
        if _HAS_YAML:
            return yaml.safe_load(s)
        else:
            # Fallback to JSON deserialization
            return json.loads(s)

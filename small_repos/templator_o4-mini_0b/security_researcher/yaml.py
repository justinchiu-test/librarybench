import json

class YAMLError(Exception):
    """Minimal YAMLError to satisfy sandbox.from_yaml error handling."""
    pass

def safe_dump(value):
    # Use JSON serialization under the hood
    return json.dumps(value)

def safe_load(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Raise our YAMLError so from_yaml(...) can propagate it
        raise YAMLError(str(e))

import json

def safe_dump(data):
    """
    Minimal YAML dump using JSON serialization for simple data structures.
    """
    return json.dumps(data)

def safe_load(s):
    """
    Minimal YAML load using JSON deserialization for simple data structures.
    """
    return json.loads(s)

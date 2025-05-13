import json

def safe_load(s):
    """
    A stand-in for yaml.safe_load using JSON parsing,
    so tests and engine code depending on yaml.safe_load will work even if PyYAML is not installed.
    """
    return json.loads(s)

def safe_dump(obj):
    """
    A stand-in for yaml.safe_dump using JSON serialization,
    so tests and engine code depending on yaml.safe_dump will work even if PyYAML is not installed.
    """
    return json.dumps(obj)

import json

def dump(obj):
    """
    Dump a Python object to a JSON-formatted string.
    Used as a stand-in for YAML dumping.
    """
    return json.dumps(obj)

def safe_load(s):
    """
    Load a Python object from a JSON-formatted string.
    Used as a stand-in for YAML safe_load.
    """
    return json.loads(s)

# alias to match PyYAML interface
load = safe_load

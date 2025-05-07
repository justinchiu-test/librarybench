import json

def safe_dump(data, *args, **kwargs):
    """
    Minimal stub for yaml.safe_dump.
    Delegates to json.dumps so tests can import and call it.
    """
    return json.dumps(data)

dump = safe_dump

def safe_load(s, *args, **kwargs):
    """
    Minimal stub for yaml.safe_load.
    Delegates to json.loads so tests can import and call it.
    """
    return json.loads(s)

load = safe_load

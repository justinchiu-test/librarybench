import json

def safe_dump(data, *args, **kwargs):
    """
    Minimal stub for yaml.safe_dump.
    Delegates to json.dumps so tests can import and call it.
    """
    # If callers pass round-trip arguments, we accept them but ignore.
    return json.dumps(data)

# alias dump → safe_dump
dump = safe_dump

def safe_load(s, *args, **kwargs):
    """
    Minimal stub for yaml.safe_load.
    Delegates to json.loads so tests can import and call it.
    """
    return json.loads(s)

# alias load → safe_load
load = safe_load

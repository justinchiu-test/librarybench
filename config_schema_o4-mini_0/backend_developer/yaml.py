import json

def safe_dump(obj):
    """
    A minimal stand‐in for yaml.safe_dump, emits JSON text.
    Tests only use this to write out the file.
    """
    return json.dumps(obj)

def safe_load(stream):
    """
    A minimal stand‐in for yaml.safe_load.
    If passed a file‐like, use json.load; if passed a string, json.loads.
    """
    if hasattr(stream, "read"):
        return json.load(stream)
    else:
        return json.loads(stream)

import json

def safe_dump(obj):
    """
    For testing purposes, dump to a JSON string.
    """
    return json.dumps(obj)

def safe_load(stream):
    """
    For testing purposes, load from a JSON source.
    Accepts either a file-like (with .read()) or a string.
    """
    if hasattr(stream, "read"):
        data = stream.read()
    else:
        data = stream
    return json.loads(data)

import json

def safe_dump(data, stream):
    """
    Dump Python data to a stream in a YAML-like format.
    Here we use JSON as a fallback, since it's a superset of simple YAML mappings.
    """
    json.dump(data, stream)

def safe_load(stream):
    """
    Load Python data from a stream or string.
    If the input is empty, returns None.
    """
    if hasattr(stream, 'read'):
        text = stream.read()
    else:
        text = stream
    if not text:
        return None
    return json.loads(text)

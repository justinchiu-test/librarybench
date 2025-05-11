import json

def dump(data):
    # Use JSON as a stand-in for YAML dumping
    return json.dumps(data)

def safe_load(stream):
    # Treat YAML as JSON for this environment
    # Accept either str or file-like; if file-like, read()
    if hasattr(stream, 'read'):
        text = stream.read()
    else:
        text = stream
    return json.loads(text)

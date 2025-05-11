import json
import io

def dumps(data):
    """
    Serialize a dict to a TOML-like string.
    Here we just emit JSON so our stub parser can read it back.
    """
    return json.dumps(data)

def loads(s):
    """
    Parse a TOML-like string.
    We'll treat it as JSON.
    """
    return json.loads(s)

def load(f):
    """
    Load from a file-like or path-like object.
    If passed a file-like, read it; otherwise assume it's a path.
    """
    # If it's a file-like object
    if hasattr(f, 'read'):
        text = f.read()
    else:
        # Treat f as a filename
        with open(f, 'r') as fp:
            text = fp.read()
    return loads(text)

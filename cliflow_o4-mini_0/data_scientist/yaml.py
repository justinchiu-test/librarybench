import json

def safe_dump(data):
    """
    Stub YAML safe_dump: emit JSON so that safe_load can read it back.
    """
    return json.dumps(data)

def safe_load(s):
    """
    Stub YAML safe_load: parse the JSON that safe_dump emitted.
    Accepts either a string or a file-like object.
    """
    # If passed a file-like object, read its contents
    try:
        # TextIOWrapper or any file-like with read()
        content = s.read()
    except Exception:
        # Not file-like, assume it's a str/bytes
        content = s
    return json.loads(content)

import json

def dump(obj):
    """
    A minimal YAML dump stub: emit JSON (which is valid YAML).
    """
    return json.dumps(obj)

def safe_load(s):
    """
    A minimal YAML load stub: parse JSON.
    If there's any non-JSON prefix (e.g. "YAML: {...}"), strip up to the first
    '{' or '[' so json.loads can succeed.
    """
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # try to find JSON start
        idx1 = s.find('{')
        idx2 = s.find('[')
        idxs = [i for i in (idx1, idx2) if i != -1]
        if not idxs:
            # no JSON structure, re-raise
            raise
        start = min(idxs)
        return json.loads(s[start:])

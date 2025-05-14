import json

def dumps(obj):
    """
    For testing purposes, dump to a TOML‐like string.
    We'll just JSON‐serialize so tests can round‐trip via our loader.
    """
    return json.dumps(obj)

def loads(s):
    """
    Load from a TOML string (actually JSON).
    """
    return json.loads(s)

def load(fp):
    """
    Load from a file‐like object; our load_toml will call this.
    """
    # JSON‐based stand‐in for TOML
    return json.load(fp)

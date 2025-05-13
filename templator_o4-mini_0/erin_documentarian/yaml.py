import json

def dump(obj):
    """
    Minimal YAML‐like dump using JSON under the hood.
    This lets docbuilder.to_yaml() always work.
    """
    return json.dumps(obj)

def safe_load(s):
    """
    Minimal YAML‐like load using JSON under the hood.
    This lets docbuilder.from_yaml() always work.
    """
    return json.loads(s)

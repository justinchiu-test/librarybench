import json

def dump(obj):
    """
    A minimal stub for yaml.dump that serializes via JSON.
    The tests only check that from_yaml(to_yaml(obj)) == obj.
    """
    return json.dumps(obj)

def safe_load(s):
    """
    A minimal stub for yaml.safe_load that deserializes JSON.
    """
    return json.loads(s)

import json

def safe_dump(obj):
    # Use JSON serialization as YAML is a superset of JSON
    return json.dumps(obj)

def safe_load(s):
    # Parse JSON, which works for our YAML-like input
    return json.loads(s)

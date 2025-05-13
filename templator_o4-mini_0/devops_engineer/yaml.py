import json

def safe_dump(obj):
    # produce a string (not real YAML, but round-trips via JSON)
    return json.dumps(obj)

def safe_load(s):
    # parse what safe_dump produced
    return json.loads(s)

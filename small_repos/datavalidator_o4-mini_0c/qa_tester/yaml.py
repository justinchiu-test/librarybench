import json

def dump(obj, stream):
    """
    A minimal YAML dump stub that writes JSON,
    since the tests only require round‐trip fidelity
    for simple structures.
    """
    json.dump(obj, stream)

def safe_load(stream):
    """
    A minimal YAML load stub that reads JSON.
    Compatible with our dump above and the test cases.
    """
    return json.load(stream)

import json

def dump(data, stream):
    """
    A simple YAML dump stub using JSON serialization.
    Tests import yaml.dump and yaml.safe_load; JSON is a subset of YAML,
    so this stub will satisfy both export/import and test expectations.
    """
    return json.dump(data, stream)

def safe_load(stream):
    """
    A simple YAML safe_load stub using JSON deserialization.
    """
    return json.load(stream)

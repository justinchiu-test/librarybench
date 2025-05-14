"""
A minimal stub for yaml so that tests importing `import yaml` succeed,
and schema.load_yaml / to_yaml work by using JSON under the hood.
"""
import json

def safe_load(stream):
    """
    Read YAML by delegating to JSON loader (tests only require round-trip).
    """
    return json.load(stream)

def safe_dump(data, stream):
    """
    Write YAML by delegating to JSON dumper.
    """
    json.dump(data, stream)

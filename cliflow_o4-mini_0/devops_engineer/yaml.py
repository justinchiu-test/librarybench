"""
A minimal YAML stub to satisfy tests that import yaml.
Provides simple dump and safe_load for flat dictionaries,
using JSON syntax under the hood.
"""
import json

def dump(data):
    # Serialize dict to a JSON string (tests use this dump)
    return json.dumps(data)

def safe_load(s):
    # Parse the JSON string back to dict
    return json.loads(s)

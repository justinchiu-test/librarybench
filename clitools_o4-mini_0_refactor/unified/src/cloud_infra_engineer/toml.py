"""
TOML stub for cloud infrastructure engineer using JSON.
"""
import json

def dump(data, file_obj):
    # Write JSON for simplicity
    json.dump(data, file_obj)

def dumps(data):
    return json.dumps(data)

def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
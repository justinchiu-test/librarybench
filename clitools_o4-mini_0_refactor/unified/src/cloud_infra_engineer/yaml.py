"""
YAML stub for cloud infrastructure engineer using JSON.
"""
import json

def dump(data):
    # Return JSON string
    return json.dumps(data)

def safe_load(file_obj):
    return json.load(file_obj)
"""
YAML wrapper for Robotics Engineer CLI
"""
import json

def dump(obj):
    return json.dumps(obj)

def safe_load(s):
    return json.loads(s)
"""
YAML support for devops_engineer.
"""
"""
YAML support stub for devops_engineer: JSON-based.
"""
import json

def safe_dump(data, file_obj):
    # Write data as JSON for simplicity
    json.dump(data, file_obj)

def safe_load(file_obj):
    # Read data from JSON stub
    return json.load(file_obj)
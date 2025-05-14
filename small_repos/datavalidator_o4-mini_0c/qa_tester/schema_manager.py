import json
import os
import yaml

def export_schema(schema, filepath):
    _, ext = os.path.splitext(filepath.lower())
    with open(filepath, 'w') as f:
        if ext in ['.yaml', '.yml']:
            yaml.dump(schema, f)
        else:
            json.dump(schema, f, indent=2)

def import_schema(filepath):
    _, ext = os.path.splitext(filepath.lower())
    with open(filepath, 'r') as f:
        if ext in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        else:
            return json.load(f)

"""
Configuration loading and validation for security analysts.
"""
import os
import json
import configparser
import security_analyst.yaml as yaml
import security_analyst.toml as toml
from security_analyst.jsonschema import ValidationError

def load_config(path, schema):
    # Determine extension
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == '.json':
            data = json.load(open(path, 'r', encoding='utf-8'))
        elif ext in ('.yml', '.yaml'):
            data = yaml.safe_load(open(path, 'r', encoding='utf-8'))
        elif ext == '.toml':
            data = toml.load(path)
        else:
            raise ValidationError(f"Unsupported file extension: {ext}")
    except FileNotFoundError:
        raise
    except Exception as e:
        raise ValidationError(str(e))
    # Validate structure
    if schema.get('type') != 'object':
        raise ValidationError('Schema type not supported')
    properties = schema.get('properties', {})
    required = schema.get('required', [])
    # check required keys
    for key in required:
        if key not in data:
            raise ValidationError(f"Missing required key: {key}")
    # check types
    for key, prop in properties.items():
        expected = prop.get('type')
        val = data.get(key)
        if expected == 'number':
            if not isinstance(val, (int, float)):
                raise ValidationError(f"Key {key} expected number")
        # more types can be added
    return data
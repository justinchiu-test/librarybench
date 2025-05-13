"""
Configuration loader for Security Analyst CLI.
"""
import os
import json
import configparser
import adapters.security_analyst.toml as toml
import adapters.security_analyst.yaml as yaml
from adapters.security_analyst.jsonschema import ValidationError

def load_config(path, schema):
    low = path.lower()
    if low.endswith('.ini'):
        cp = configparser.ConfigParser()
        cp.read(path)
        data = {sec: dict(cp[sec]) for sec in cp.sections()}
    elif low.endswith('.json'):
        with open(path, 'r') as f:
            data = json.load(f)
    elif low.endswith(('.yaml', '.yml')):
        # simple YAML parsing
        data = {}
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    k, v = line.split(':', 1)
                    val = v.strip()
                    data[k.strip()] = int(val) if val.isdigit() else val
    elif low.endswith('.toml'):
        # simple TOML flat mapping
        data = {}
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('['):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    key = k.strip()
                    val = v.strip().strip("'\"")
                    data[key] = int(val) if val.isdigit() else val
    else:
        data = {}
    # Validate
    from adapters.security_analyst.cli_framework.validation import validate_input as validate
    # data may need flattening if INI nested
    # For simplicity, treat missing or wrong types as errors
    for key in schema.get('required', []):
        if key not in data:
            raise ValidationError(f"Missing key: {key}")
    for key, prop in schema.get('properties', {}).items():
        if key in data and prop.get('type'):
            t = prop.get('type')
            val = data[key]
            if t == 'number' and not isinstance(val, (int, float)):
                raise ValidationError(f"Type mismatch: {key}")
    return data
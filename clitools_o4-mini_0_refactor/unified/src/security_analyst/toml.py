"""
Minimal TOML parser for security analysts.
"""
"""
Minimal TOML support for security analysts.
Supports JSON content and simple key=value pairs.
"""
import os
import json

def dump(data, file_obj):
    # Write data as JSON
    json.dump(data, file_obj)

def load(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    stripped = content.lstrip()
    # Detect JSON content
    if stripped.startswith('{') or stripped.startswith('['):
        return json.loads(content)
    # Simple TOML-style key = value parsing
    data = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip()
            # parse number
            if val.isdigit():
                data[key] = int(val)
            else:
                try:
                    data[key] = float(val)
                except ValueError:
                    # strip quotes
                    data[key] = val.strip('"')
    return data
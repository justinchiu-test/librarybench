"""
Simple TOML parser/dumper for Security Analyst CLI.
"""
import os

def load(path):
    lines = open(path, 'r').read().splitlines()
    result = {}
    current = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1]
            parts = section.split('.')
            current = result
            for part in parts:
                current = current.setdefault(part, {})
        elif '=' in line and current is not None:
            key, val = line.split('=', 1)
            key = key.strip()
            v = val.strip().strip('"').strip("'")
            current[key] = v
    return result

def dumps(data):
    """Serialize nested dict `data` as TOML with tables."""
    out = ''
    # Handle two-level nested sections for tool.poetry and its dependencies
    for top, mapping in data.items():
        if isinstance(mapping, dict):
            for sub, submap in mapping.items():
                # First-level table
                out += f"[{top}.{sub}]\n"
                # Basic key-values (exclude nested dicts)
                for key, val in submap.items():
                    if not isinstance(val, dict):
                        out += f"{key} = \"{val}\"\n"
                # Nested tables for dict values
                for key, val in submap.items():
                    if isinstance(val, dict):
                        out += f"[{top}.{sub}.{key}]\n"
                        for k2, v2 in val.items():
                            out += f"{k2} = \"{v2}\"\n"
        else:
            # Flat key
            out += f"{top} = \"{mapping}\"\n"
    return out
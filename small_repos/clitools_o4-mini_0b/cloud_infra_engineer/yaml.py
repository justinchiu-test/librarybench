"""
Minimal YAML stub for safe_load and dump.
"""
import json

def safe_load(s):
    result = {}
    for line in s.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            # try to parse as JSON for numbers, booleans, etc.
            try:
                parsed = json.loads(val)
            except Exception:
                parsed = val
            result[key] = parsed
    return result

def dump(obj):
    if isinstance(obj, dict):
        lines = []
        for key, val in obj.items():
            lines.append(f"{key}: {val}")
        return "\n".join(lines) + "\n"
    raise TypeError("Unsupported type for dump")

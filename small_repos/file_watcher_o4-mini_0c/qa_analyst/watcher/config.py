import json
import os

try:
    import yaml
except ImportError:
    yaml = None

try:
    import toml
except ImportError:
    toml = None

# Fallback to Python 3.11's tomllib if external toml not available
try:
    import tomllib
except ImportError:
    tomllib = None

if toml is None and tomllib is not None:
    toml = tomllib  # tomllib has loads()

def load_config(path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, 'r') as f:
        data = f.read()
    if ext in ['.yaml', '.yml']:
        if yaml:
            return yaml.safe_load(data)
        # Minimal YAML safe loader for simple mappings/lists
        cfg = {}
        for line in data.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' not in line:
                continue
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            # Try JSON parse for lists, numbers, booleans, etc.
            try:
                parsed = json.loads(val)
            except Exception:
                parsed = val
            cfg[key] = parsed
        return cfg
    elif ext == '.json':
        return json.loads(data)
    elif ext == '.toml':
        if not toml:
            raise ImportError("toml required for TOML support")
        # toml library and tomllib both offer loads()
        return toml.loads(data)
    else:
        raise ValueError(f"Unsupported config format: {ext}")

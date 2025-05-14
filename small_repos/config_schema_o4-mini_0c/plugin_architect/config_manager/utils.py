import os

try:
    import yaml
except ImportError:
    yaml = None

def load_yaml(path):
    if yaml is None:
        raise ImportError("PyYAML is required for load_yaml")
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def load_dotenv(path):
    data = {}
    if not os.path.exists(path):
        return data
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, val = line.split('=', 1)
            data[key.strip()] = val.strip()
    return data

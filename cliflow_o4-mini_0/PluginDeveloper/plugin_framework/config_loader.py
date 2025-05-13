import os
import json
import configparser

try:
    import yaml
except ImportError:
    yaml = None

try:
    import toml
except ImportError:
    toml = None

def load_config(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    elif ext in ('.yaml', '.yml'):
        if yaml is None:
            raise RuntimeError('YAML support not available')
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    elif ext == '.toml':
        if toml is None:
            raise RuntimeError('TOML support not available')
        with open(path, 'r') as f:
            return toml.loads(f.read())
    elif ext in ('.ini',):
        cp = configparser.ConfigParser()
        cp.read(path)
        return {s: dict(cp.items(s)) for s in cp.sections()}
    else:
        raise ValueError('Unsupported config format: ' + ext)

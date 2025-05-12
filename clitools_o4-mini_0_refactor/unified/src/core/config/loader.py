"""
Load and merge configuration from files and strings.
"""
import os
import json
from configparser import ConfigParser
try:
    import yaml
except ImportError:
    yaml = None
try:
    import toml
except ImportError:
    toml = None

def load_config(paths):
    # Accept single path or list
    if isinstance(paths, str):
        paths = [paths]
    config = {}
    for path in paths:
        ext = os.path.splitext(path)[1].lower()
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if ext == '.json':
                    data = json.load(f)
                elif ext in ('.ini', '.cfg'):
                    cp = ConfigParser()
                    cp.read_file(f)
                    sections = cp.sections()
                    if len(sections) == 1 and sections[0].lower() == 'default':
                        data = dict(cp['default'])
                    else:
                        data = {sec: dict(cp[sec]) for sec in sections}
                elif ext in ('.yml', '.yaml') and yaml:
                    data = yaml.safe_load(f)
                elif ext == '.toml' and toml:
                    data = toml.load(f)
                else:
                    continue
        except Exception:
            continue
        # merge dictionaries
        if isinstance(data, dict):
            for key, val in data.items():
                if key in config and isinstance(config[key], dict) and isinstance(val, dict):
                    config[key].update(val)
                else:
                    config[key] = val
    return config

def parse_config_string(s, fmt):
    fmt = fmt.lower()
    if fmt == 'json':
        return json.loads(s)
    elif fmt in ('ini', 'cfg'):
        cp = ConfigParser()
        cp.read_string(s)
        data = {}
        for sec in cp.sections():
            data[sec] = dict(cp[sec])
        return data
    elif fmt in ('yaml', 'yml'):
        if not yaml:
            raise ImportError('PyYAML not available')
        return yaml.safe_load(s)
    elif fmt == 'toml':
        if not toml:
            raise ImportError('toml not available')
        return toml.loads(s)
    else:
        raise ValueError(f'Unknown format: {fmt}')
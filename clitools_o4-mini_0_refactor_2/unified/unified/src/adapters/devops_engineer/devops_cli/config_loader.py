"""
Load configuration files for DevOps Engineer CLI.
Supports INI, JSON, YAML, TOML.
"""
import json
import configparser
from . import yaml, toml

def load_config(paths):
    result = {}
    for p in paths:
        low = p.lower()
        if low.endswith('.ini'):
            cp = configparser.ConfigParser()
            cp.read(p)
            for section in cp.sections():
                result.setdefault(section, {})
                for k, v in cp[section].items():
                    result[section][k] = v
        elif low.endswith('.json'):
            data = json.load(open(p, 'r'))
            if isinstance(data, dict):
                for k, v in data.items():
                    result[k] = v
        elif low.endswith(('.yaml', '.yml')):
            data = yaml.safe_load(open(p, 'r'))
            if isinstance(data, dict):
                for k, v in data.items():
                    result[k] = v
        elif low.endswith('.toml'):
            data = toml.load(open(p, 'r'))
            if isinstance(data, dict):
                for k, v in data.items():
                    result[k] = v
    return result
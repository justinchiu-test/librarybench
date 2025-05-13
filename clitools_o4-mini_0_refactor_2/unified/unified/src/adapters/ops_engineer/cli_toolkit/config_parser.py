"""
Parse configuration strings for Operations Engineer CLI.
Supports JSON, INI, YAML, TOML.
"""
import json
import configparser

def parse_config_string(s, fmt):
    if fmt == 'json':
        return json.loads(s)
    elif fmt == 'ini':
        cp = configparser.ConfigParser()
        cp.read_string(s)
        return {sec: dict(cp[sec]) for sec in cp.sections()}
    elif fmt == 'yaml':
        import yaml
        return yaml.safe_load(s)
    elif fmt == 'toml':
        import toml
        return toml.loads(s)
    else:
        raise ValueError(f"Unknown format: {fmt}")

def merge_dicts(a, b):
    result = dict(a)
    for k, v in b.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = merge_dicts(result[k], v)
        else:
            result[k] = v
    return result
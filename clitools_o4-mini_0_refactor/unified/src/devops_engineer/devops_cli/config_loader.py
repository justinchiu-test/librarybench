"""
Load and merge configuration files for devops engineers.
"""
import os
import json
import configparser
import devops_engineer.yaml as yaml
import devops_engineer.toml as toml

def load_config(paths):
    # Accept single path or list
    if isinstance(paths, str):
        paths = [paths]
    config = {}
    for path in paths:
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == '.json':
                data = json.load(open(path, 'r', encoding='utf-8'))
            elif ext in ('.ini', '.cfg'):
                cp = configparser.ConfigParser()
                cp.read(path)
                data = {sec: dict(cp[sec]) for sec in cp.sections()}
            elif ext in ('.yml', '.yaml'):
                data = yaml.safe_load(open(path, 'r', encoding='utf-8'))
            elif ext == '.toml':
                data = toml.load(path)
            else:
                continue
        except Exception:
            continue
        if isinstance(data, dict):
            for key, val in data.items():
                config[key] = val
    return config
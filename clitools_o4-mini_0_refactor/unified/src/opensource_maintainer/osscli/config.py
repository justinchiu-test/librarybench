"""
Configuration loader for open-source maintainers.
"""
import os
import json
import configparser

def load_config(paths):
    if isinstance(paths, str):
        paths = [paths]
    config = {}
    # load ini and json
    for path in paths:
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext in ('.ini', '.cfg'):
                cp = configparser.ConfigParser()
                cp.read(path)
                for sec in cp.sections():
                    config[sec] = dict(cp[sec])
            elif ext == '.json':
                data = json.load(open(path, 'r', encoding='utf-8'))
                for k, v in data.items():
                    config[k] = v
        except Exception:
            continue
    # environment overrides
    for key, val in os.environ.items():
        if key.startswith('OSS_'):
            config[key[4:].lower()] = val
    return config
"""
Configuration loader for Open Source Maintainer CLI.
"""
import os
import json
import configparser

def load_config(paths):
    result = {}
    for p in paths:
        low = p.lower()
        if low.endswith('.ini'):
            cp = configparser.ConfigParser()
            cp.read(p)
            for sec in cp.sections():
                result.setdefault(sec, {})
                for k, v in cp[sec].items():
                    result[sec][k] = v
        elif low.endswith('.json'):
            data = json.load(open(p, 'r'))
            if isinstance(data, dict):
                for k, v in data.items():
                    result[k] = v
    # Environment overrides: include values for any OSS_ vars
    for env_key, val in os.environ.items():
        if env_key.startswith('OSS_'):
            k = env_key[len('OSS_'):]
            result[k] = val
    return result
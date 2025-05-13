"""
Configuration parser for data_scientist datapipeline CLI.
"""
import json
import configparser

def parse_config_files(paths):
    result = {}
    for p in paths:
        low = p.lower()
        if low.endswith('.json'):
            with open(p, 'r') as f:
                data = json.load(f)
            if isinstance(data, dict):
                result.update(data)
        elif low.endswith('.ini'):
            cp = configparser.ConfigParser()
            cp.read(p)
            if 'default' in cp:
                result.update(dict(cp['default']))
    return result
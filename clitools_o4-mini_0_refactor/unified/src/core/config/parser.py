import json
import os
from configparser import ConfigParser

def parse_config_files(paths):
    # normalize input
    if isinstance(paths, str):
        paths = [paths]
    result = {}
    for path in paths:
        _, ext = os.path.splitext(path)
        ext = ext.lower()
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
                else:
                    continue
        except (FileNotFoundError, ValueError):
            continue
        # merge
        for key, val in data.items():
            if key in result and isinstance(result[key], dict) and isinstance(val, dict):
                result[key].update(val)
            else:
                result[key] = val
    return result
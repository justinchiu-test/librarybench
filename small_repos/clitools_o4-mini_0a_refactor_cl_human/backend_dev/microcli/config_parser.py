import json
import configparser
import os

def parse_config_files(paths: list) -> dict:
    result = {}
    for path in paths:
        if not os.path.isfile(path):
            continue
        ext = os.path.splitext(path)[1].lower()
        if ext == ".json":
            with open(path) as f:
                data = json.load(f)
        elif ext in (".ini", ".cfg"):
            cp = configparser.ConfigParser()
            cp.read(path)
            data = {s: dict(cp[s]) for s in cp.sections()}
        else:
            continue
        # merge shallow
        result.update(data)
    return result

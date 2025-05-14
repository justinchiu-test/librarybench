import configparser
import json
import toml
import yaml
import os

def load_config(file_paths):
    merged = {}
    for path in file_paths:
        if not os.path.exists(path):
            continue
        ext = os.path.splitext(path)[1].lower()
        if ext == ".ini":
            cp = configparser.ConfigParser()
            cp.read(path)
            data = {s: dict(cp.items(s)) for s in cp.sections()}
        elif ext == ".json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        elif ext in (".yml", ".yaml"):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        elif ext == ".toml":
            # tomllib requires a binary file
            with open(path, "rb") as f:
                data = toml.load(f)
        else:
            continue
        # shallow merge
        for k, v in data.items():
            merged[k] = v
    return merged

import json
import yaml
import toml
from jsonschema import validate

def load_config(path, schema):
    if path.endswith(".json"):
        with open(path) as f:
            data = json.load(f)
    elif path.endswith((".yml", ".yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
    elif path.endswith(".toml"):
        with open(path) as f:
            data = toml.load(f)
    else:
        raise ValueError("Unsupported config format")
    validate(instance=data, schema=schema)
    return data

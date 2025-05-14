import json
import os

try:
    import yaml
except ImportError:
    yaml = None

try:
    import toml
except ImportError:
    toml = None

class ConfigFileSupport:
    @staticmethod
    def load(path):
        """
        Load a configuration file from JSON, YAML, or TOML.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        ext = os.path.splitext(path)[1].lower()
        with open(path, 'r') as f:
            data = f.read()
        if ext == '.json':
            return json.loads(data)
        elif ext in ('.yml', '.yaml'):
            if yaml is None:
                raise RuntimeError("PyYAML is required to load YAML files")
            return yaml.safe_load(data)
        elif ext == '.toml':
            if toml is None:
                raise RuntimeError("toml module is required to load TOML files")
            return toml.loads(data)
        else:
            raise ValueError(f"Unsupported config file type: {ext}")

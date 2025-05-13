import json
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
        if path.endswith('.json'):
            with open(path) as f:
                return json.load(f)
        elif path.endswith(('.yaml', '.yml')):
            if yaml is None:
                raise RuntimeError('yaml library not available')
            with open(path) as f:
                return yaml.safe_load(f)
        elif path.endswith('.toml'):
            if toml is None:
                raise RuntimeError('toml library not available')
            with open(path) as f:
                return toml.load(f)
        else:
            raise ValueError('Unsupported config format: ' + path)

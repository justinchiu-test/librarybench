import json

try:
    import yaml
except ImportError:
    yaml = None

class ConfigFileSupport:
    @staticmethod
    def load_config(path):
        with open(path, "r") as f:
            content = f.read()
        try:
            if path.endswith((".yaml", ".yml")):
                if not yaml:
                    raise ValueError("YAML support not available")
                return yaml.safe_load(content)
            else:
                return json.loads(content)
        except Exception as e:
            raise ValueError(f"Failed to load config: {e}")

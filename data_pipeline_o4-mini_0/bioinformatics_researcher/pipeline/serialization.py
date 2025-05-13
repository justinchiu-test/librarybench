import json

try:
    import yaml
    _yaml_available = True
except ImportError:
    _yaml_available = False

class JSONSerializer:
    @staticmethod
    def serialize(data):
        return json.dumps(data)

class YAMLSerializer:
    @staticmethod
    def serialize(data):
        if _yaml_available:
            return yaml.safe_dump(data)
        # Basic fallback YAML serialization for simple structures
        lines = []
        def _dump(item, indent=0):
            if isinstance(item, dict):
                for k, v in item.items():
                    if isinstance(v, (dict, list)):
                        lines.append(' ' * indent + f"{k}:")
                        _dump(v, indent + 2)
                    else:
                        lines.append(' ' * indent + f"{k}: {v}")
            elif isinstance(item, list):
                for elem in item:
                    if isinstance(elem, (dict, list)):
                        lines.append(' ' * indent + "-")
                        _dump(elem, indent + 2)
                    else:
                        lines.append(' ' * indent + f"- {elem}")
            else:
                lines.append(' ' * indent + str(item))

        _dump(data)
        # Ensure trailing newline for readability
        return "\n".join(lines) + "\n"

import json
import base64

def export_data(data, fmt="json", encrypt=False):
    if fmt == "json":
        raw = json.dumps(data)
    elif fmt == "yaml":
        # Minimal YAML serializer for flat dicts
        lines = []
        for k, v in data.items():
            lines.append(f"{k}: {v}")
        raw = "\n".join(lines)
    else:
        raise ValueError("Unsupported format")
    if encrypt:
        token = base64.b64encode(raw.encode()).decode()
        return token
    return raw

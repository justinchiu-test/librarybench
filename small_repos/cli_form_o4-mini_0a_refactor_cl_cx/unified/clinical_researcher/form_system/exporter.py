import json

def export_data(data, format='json'):
    """
    Export data as json, yaml, or python dict (returns the dict itself).
    """
    fmt = format.lower()
    if fmt == 'json':
        return json.dumps(data)
    elif fmt == 'yaml':
        # Simple YAML-like serialization without external dependencies
        lines = []
        for key, value in data.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)
    elif fmt == 'python':
        return data
    else:
        raise ValueError(f"Unsupported export format: {format}")

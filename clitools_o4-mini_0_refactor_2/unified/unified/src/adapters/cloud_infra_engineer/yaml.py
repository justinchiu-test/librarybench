"""
Simple YAML dump for Cloud Infrastructure Engineer CLI.
"""
def dump(data):
    """Serialize a dict `data` as simple YAML string."""
    out = ''
    for k, v in data.items():
        out += f"{k}: {v}\n"
    return out
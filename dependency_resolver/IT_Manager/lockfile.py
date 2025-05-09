import json

def generate_lockfile(installed_map, filepath):
    """
    installed_map: dict name->version_str
    Writes JSON to filepath.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(installed_map, f, indent=2)

def load_lockfile(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

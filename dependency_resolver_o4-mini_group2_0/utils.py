import os
import json

def load_json(path):
    """Load JSON data from a file."""
    with open(path, "r") as f:
        return json.load(f)

def dump_json(data, path, indent=2):
    """Write JSON data to a file."""
    # ensure the directory exists
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=indent)

def ensure_dir(path):
    """Create a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def remove_file(path, not_exist_msg=None):
    """Remove a file, raising FileNotFoundError with a custom message if missing."""
    if not os.path.isfile(path):
        msg = not_exist_msg or f"No such file: {path}"
        raise FileNotFoundError(msg)
    os.remove(path)

def list_json_files(dir_path):
    """Return sorted basenames (without .json) of all JSON files in a directory."""
    try:
        files = os.listdir(dir_path)
    except FileNotFoundError:
        return []
    return sorted(os.path.splitext(f)[0] for f in files if f.endswith(".json"))

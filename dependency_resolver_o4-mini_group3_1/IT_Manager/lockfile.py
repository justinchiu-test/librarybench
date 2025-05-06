from utils import write_json, read_json

def generate_lockfile(installed_map, filepath):
    """
    installed_map: dict name->version_str
    Writes JSON to filepath.
    """
    write_json(filepath, installed_map, indent=2)

def load_lockfile(filepath):
    return read_json(filepath)

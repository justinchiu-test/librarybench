import os
import json
import shutil
import time

def ensure_dir(path):
    """Create directory if it does not exist."""
    os.makedirs(path, exist_ok=True)

def ensure_file(path, default):
    """Ensure a file exists; if not, create it with default JSON content."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(path):
        write_json(path, default)

def load_json(path):
    """Load JSON content from a file."""
    with open(path, 'r') as f:
        return json.load(f)

def write_json(path, data, indent=2):
    """Write data as JSON to a file."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    # if indent is None, JSON writes compactly
    with open(path, 'w') as f:
        json.dump(data, f, indent=indent)

def remove_file(path):
    """Remove a file if it exists."""
    if os.path.exists(path):
        os.remove(path)

def list_dirs(path):
    """List immediate subdirectories of a directory."""
    return [name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name))]

def copy_file(src, dst):
    """Copy a file, creating destination dir as needed."""
    d = os.path.dirname(dst)
    if d:
        os.makedirs(d, exist_ok=True)
    shutil.copy2(src, dst)

def time_ns():
    """Return current time in nanoseconds."""
    return time.time_ns()

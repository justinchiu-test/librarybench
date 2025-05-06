import os
import json
import shutil
import time

def ensure_dir(path):
    """Ensure that a directory exists."""
    os.makedirs(path, exist_ok=True)

def read_json(path):
    """Read JSON data from a file."""
    with open(path, 'r') as f:
        return json.load(f)

def write_json(path, data, indent=2):
    """Write Python data as JSON to a file."""
    ensure_dir(os.path.dirname(path))
    with open(path, 'w') as f:
        json.dump(data, f, indent=indent)

def copy_file(src, dst):
    """Copy a file, creating destination dirs if needed."""
    ensure_dir(os.path.dirname(dst))
    shutil.copy2(src, dst)

def list_dirs(path):
    """List sorted subdirectories of a directory."""
    return sorted(
        d for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d))
    )

def write_text(path, text):
    """Write text to a file, creating parent dirs if needed."""
    ensure_dir(os.path.dirname(path))
    with open(path, 'w') as f:
        f.write(text)

def read_text(path):
    """Read and return text from a file."""
    with open(path, 'r') as f:
        return f.read()

def get_timestamp_ns():
    """Get current high-resolution timestamp as string."""
    return str(time.time_ns())

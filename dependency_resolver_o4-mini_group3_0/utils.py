import os
import json
import shutil
import tarfile
import re

def ensure_dirs(paths):
    """Ensure a list of directories exist."""
    for d in paths:
        os.makedirs(d, exist_ok=True)

def read_json(path):
    """Load JSON data from a file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(data, path, indent=2):
    """Write JSON data to a file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)

def copy_tree(src, dst):
    """Copy an entire directory tree."""
    shutil.copytree(src, dst)

def remove_path(path):
    """Remove a file or directory tree."""
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)

def list_numeric_dirs(path):
    """List directory entries that are numeric names."""
    return [n for n in os.listdir(path) if n.isdigit()]

def get_next_index(path):
    """Return the next numeric index for naming snapshots."""
    nums = [int(n) for n in list_numeric_dirs(path)] or [0]
    return max(nums) + 1

def parse_version(v):
    """Convert a version string 'x.y.z' into a tuple of ints."""
    return tuple(int(x) for x in v.split('.'))

def version_satisfies(v, constraint):
    """
    Check if version string v satisfies a constraint like '>=1.0' or '==2.0'.
    """
    m = re.match(r'(>=|==)(.+)', constraint or '')
    if not m:
        return False
    op, ver = m.group(1), m.group(2)
    v_t, ver_t = parse_version(v), parse_version(ver)
    if op == '==':
        return v_t == ver_t
    if op == '>=':
        return v_t >= ver_t
    return False

def find_latest_tar(dir_path, name, constraint=None):
    """
    In dir_path, find files matching 'name-version.tar.gz' and return the
    highest version that satisfies constraint, or None.
    """
    candidates = []
    pattern = rf'^{re.escape(name)}-([\d\.]+)\.tar\.gz$'
    for fn in os.listdir(dir_path):
        m = re.match(pattern, fn)
        if not m:
            continue
        ver = m.group(1)
        if constraint and not version_satisfies(ver, constraint):
            continue
        candidates.append((parse_version(ver), ver, os.path.join(dir_path, fn)))
    if not candidates:
        return None
    _, ver, path = sorted(candidates)[-1]
    return {'name': name, 'version': ver, 'path': path}

def extract_tar(tar_path, dst):
    """Extract a .tar.gz archive to the destination directory."""
    os.makedirs(dst, exist_ok=True)
    with tarfile.open(tar_path, 'r:gz') as tf:
        tf.extractall(dst)

def parse_requirement(req):
    """
    Parse a requirement string like 'pkg>=1.0' or 'pkg==2.0' or 'pkg'.
    Returns (pkg_name, constraint) or (None, None) if invalid.
    """
    m = re.match(r'^([^=<>]+?)(?:(>=|==)(.+))?$', req)
    if not m:
        return None, None
    name = m.group(1)
    constraint = (m.group(2) + m.group(3)) if m.group(2) else None
    return name, constraint

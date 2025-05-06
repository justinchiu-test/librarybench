import os
import json
import shutil
import tarfile
import re

def read_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def write_json(path, data, indent=2):
    with open(path, 'w') as f:
        json.dump(data, f, indent=indent)

def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def list_dirs(path):
    return [d for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d))]

def remove_tree(path):
    if os.path.isdir(path):
        shutil.rmtree(path)

def copy_tree(src, dst):
    shutil.copytree(src, dst)

def extract_tar(src, dst):
    with tarfile.open(src, 'r:gz') as tf:
        tf.extractall(dst)

def parse_requirement(req):
    """
    Returns (name, constraint) or (None, None) if invalid.
    """
    m = re.match(r'^([^=<>]+?)(?:(>=|==)(.+))?$', req)
    if not m:
        return None, None
    name = m.group(1)
    constraint = (m.group(2) + m.group(3)) if m.group(2) else None
    return name, constraint

def find_tar_candidates(directory, name, constraint=None, version_satisfies=None):
    """
    Finds all .tar.gz files in 'directory' matching 'name-version.tar.gz'.
    Returns list of (version_str, full_path).
    """
    candidates = []
    for fn in os.listdir(directory):
        m = re.match(rf'^{re.escape(name)}-([\d\.]+)\.tar\.gz$', fn)
        if not m:
            continue
        ver = m.group(1)
        if constraint and version_satisfies and not version_satisfies(ver, constraint):
            continue
        candidates.append((ver, os.path.join(directory, fn)))
    return candidates

def pick_highest(candidates, parse_version):
    """
    Given list of (version_str, path), returns (version_str, path) of highest version.
    """
    if not candidates:
        return None, None
    parsed = [(parse_version(ver), ver, path) for ver, path in candidates]
    _, ver, path = sorted(parsed)[-1]
    return ver, path

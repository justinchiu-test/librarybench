"""
Version management for data_scientist datapipeline CLI.
"""
import os

VERSION_FILE = 'version.txt'

def get_version():
    if not os.path.exists(VERSION_FILE):
        return '0.0.0'
    ver = open(VERSION_FILE).read().strip()
    return ver

def bump_version():
    ver = get_version()
    parts = ver.split('.')
    if not all(p.isdigit() for p in parts):
        raise ValueError(f"Invalid version format: {ver}")
    if len(parts) == 2:
        parts.append('0')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {ver}")
    major, minor, patch = map(int, parts)
    patch += 1
    new = f"{major}.{minor}.{patch}"
    with open(VERSION_FILE, 'w') as f:
        f.write(new)
    return new
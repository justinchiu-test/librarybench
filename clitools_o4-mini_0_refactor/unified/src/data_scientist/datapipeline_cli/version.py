"""
Version management for data scientists.
"""
import os

VERSION_FILE = 'version.txt'

def get_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return '0.0.0'

def bump_version():
    v = get_version()
    parts = v.split('.')
    if not all(p.isdigit() for p in parts):
        raise ValueError('Invalid version format')
    if len(parts) == 2:
        parts.append('0')
    major, minor, patch = parts
    new_patch = int(patch) + 1
    new_v = f"{major}.{minor}.{new_patch}"
    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
        f.write(new_v)
    return new_v
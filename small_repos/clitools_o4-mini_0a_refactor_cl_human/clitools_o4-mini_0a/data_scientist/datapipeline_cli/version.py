import os

VERSION_FILE = os.environ.get('VERSION_FILE', 'version.txt')

def get_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as f:
            return f.read().strip()
    return '0.0.0'

def bump_version():
    version = get_version()
    parts = version.split('.')
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError('Invalid version format')
    major, minor, patch = map(int, parts)
    patch += 1
    new_version = f'{major}.{minor}.{patch}'
    with open(VERSION_FILE, 'w') as f:
        f.write(new_version)
    return new_version

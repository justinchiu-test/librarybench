"""
Bump version based on git tags for devops engineers.
"""
import subprocess

def bump_version():
    # get latest tags
    try:
        result = subprocess.run(['git', 'tag', '--sort=-v:refname'], capture_output=True, text=True, check=False)
        tags = result.stdout.strip().splitlines()
        latest = tags[0].lstrip('v') if tags else '0.0.0'
    except Exception:
        latest = '0.0.0'
    parts = latest.split('.')
    if len(parts) == 2:
        parts.append('0')
    try:
        major, minor, patch = parts
        new_patch = int(patch) + 1
    except Exception:
        raise ValueError('Invalid tag format')
    new_version = f"{major}.{minor}.{new_patch}"
    # create new tag
    subprocess.run(['git', 'tag', new_version], capture_output=True, text=True, check=False)
    return new_version
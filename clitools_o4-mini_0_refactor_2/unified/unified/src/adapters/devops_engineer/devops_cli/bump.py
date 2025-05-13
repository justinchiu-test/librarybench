"""
Bump version utility for DevOps Engineer CLI.
"""
import subprocess
import re

def bump_version():
    # Get existing tags
    try:
        result = subprocess.run(
            ['git', 'tag', '--sort=-v:refname'], capture_output=True, text=True
        )
        tags = result.stdout.splitlines()
    except Exception:
        tags = []
    ver = None
    for tag in tags:
        if tag.startswith('v') and re.match(r'^v\d+\.\d+\.\d+$', tag):
            ver = tag.lstrip('v')
            break
    if ver is None:
        parts = [0, 0, 0]
    else:
        parts = list(map(int, ver.split('.')))
    major, minor, patch = parts if len(parts) == 3 else (parts[0], parts[1], 0)
    patch += 1
    new = f"{major}.{minor}.{patch}"
    new_tag = f"v{new}"
    # Create new tag
    subprocess.run(['git', 'tag', new_tag], capture_output=True, text=True)
    return new
"""
Version bumping for Operations Engineer CLI.
"""
import re

def bump_version(tags):
    latest = None
    for tag in tags:
        m = re.match(r'^v(\d+)\.(\d+)\.(\d+)$', tag)
        if m:
            nums = tuple(map(int, m.groups()))
            if latest is None or nums > latest:
                latest = nums
    if latest is None:
        return 'v0.0.1'
    major, minor, patch = latest
    patch += 1
    return f"v{major}.{minor}.{patch}"
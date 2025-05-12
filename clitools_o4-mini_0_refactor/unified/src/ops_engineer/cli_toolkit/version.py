"""
Version bumping for ops engineers.
"""
def bump_version(tags):
    # tags: list of tag strings, e.g. ['v1.2.3']
    versions = []
    for t in tags:
        if isinstance(t, str) and t.startswith('v'):
            parts = t[1:].split('.')
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                versions.append(tuple(int(p) for p in parts))
    if versions:
        latest = max(versions)
        major, minor, patch = latest
        new_patch = patch + 1
        return f"v{major}.{minor}.{new_patch}"
    # default
    return 'v0.0.1'
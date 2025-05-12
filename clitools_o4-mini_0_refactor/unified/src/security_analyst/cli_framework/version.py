"""
Version bumping for security analysts.
"""
def bump_version(tags):
    # tags: list of tag strings, e.g. ['1.2.3']
    versions = []
    for t in tags:
        parts = t.split('.')
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            versions.append(tuple(int(p) for p in parts))
    if versions:
        latest = max(versions)
        major, minor, patch = latest
        return f"{major}.{minor}.{patch+1}"
    # default initial version
    return '0.0.1'
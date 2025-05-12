"""
Version management for backend developers.
"""
def bump_version(version):
    parts = version.split('.')
    if not all(p.isdigit() for p in parts):
        raise ValueError("Invalid version format")
    if len(parts) == 2:
        parts.append('0')
    major, minor, patch = parts
    try:
        new_patch = int(patch) + 1
    except ValueError:
        raise ValueError("Invalid patch number")
    return f"{major}.{minor}.{new_patch}"
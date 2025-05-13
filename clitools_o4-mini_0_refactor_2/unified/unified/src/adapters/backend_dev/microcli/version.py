"""
Version bump utility for backend_dev microcli.
"""
def bump_version(ver):
    """
    Bump patch part of semantic version string.
    """
    parts = ver.split('.')
    if not all(p.isdigit() for p in parts):
        raise ValueError(f"Invalid version format: {ver}")
    if len(parts) == 2:
        parts.append('0')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {ver}")
    major, minor, patch = map(int, parts)
    patch += 1
    return f"{major}.{minor}.{patch}"
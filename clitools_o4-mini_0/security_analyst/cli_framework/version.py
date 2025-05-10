import re
from packaging.version import Version, InvalidVersion

def bump_version(tags):
    """
    Given a list of tag strings, find the latest semantic version and bump patch.
    If none, start at 0.0.1.
    """
    versions = []
    for tag in tags:
        try:
            v = Version(tag)
            versions.append(v)
        except InvalidVersion:
            continue
    if versions:
        latest = max(versions)
        new_version = Version(f"{latest.major}.{latest.minor}.{latest.micro + 1}")
    else:
        new_version = Version("0.0.1")
    return str(new_version)

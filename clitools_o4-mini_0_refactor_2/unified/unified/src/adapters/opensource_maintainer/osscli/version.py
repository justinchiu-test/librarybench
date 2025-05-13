"""
Version bump for Open Source Maintainer CLI.
"""
import re

def bump_version(file_path):
    # Read __version__ from file and increment patch
    text = open(file_path, 'r').read()
    match = re.search(r"__version__\s*=\s*['\"](\d+)\.(\d+)\.(\d+)['\"]", text)
    if not match:
        raise ValueError("Invalid version file")
    major, minor, patch = map(int, match.groups())
    patch += 1
    new = f"{major}.{minor}.{patch}"
    # Replace version in file
    new_text = re.sub(
        r"(__version__\s*=\s*['\"])(\d+\.\d+\.\d+)(['\"])",
        lambda m: m.group(1) + new + m.group(3),
        text
    )
    open(file_path, 'w').write(new_text)
    return new
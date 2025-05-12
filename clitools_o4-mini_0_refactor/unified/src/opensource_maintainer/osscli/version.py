"""
Version bump for open-source maintainers.
"""
import re

def bump_version(version_file):
    # version_file: path to Python file containing __version__
    content = open(version_file, 'r', encoding='utf-8').read()
    m = re.search(r"__version__\s*=\s*['\"](\d+)\.(\d+)\.(\d+)['\"]", content)
    if not m:
        raise ValueError('Version string not found')
    major, minor, patch = map(int, m.groups())
    patch += 1
    new_version = f"{major}.{minor}.{patch}"
    # replace version in file
    new_content = re.sub(
        r"__version__\s*=\s*['\"][^'\"]+['\"]",
        f"__version__ = '{new_version}'",
        content
    )
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return new_version
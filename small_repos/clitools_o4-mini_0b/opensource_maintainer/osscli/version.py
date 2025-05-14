import re
import os

__version__ = "0.0.1"

def bump_version(version_file=None):
    if version_file is None:
        here = os.path.dirname(__file__)
        version_file = os.path.join(here, "version.py")
    # Read the existing version.py content
    text = open(version_file).read()
    # Find the current version numbers
    m = re.search(r"__version__\s*=\s*['\"](\d+)\.(\d+)\.(\d+)['\"]", text)
    if not m:
        raise ValueError("Version string not found")
    major, minor, patch = map(int, m.groups())
    patch += 1
    new_version = f"{major}.{minor}.{patch}"
    # Replace the version line with the bumped version
    # This will standardize on single quotes, but tests only check for the new number
    new_text = re.sub(
        r"__version__\s*=\s*['\"]\d+\.\d+\.\d+['\"]",
        f"__version__ = '{new_version}'",
        text
    )
    with open(version_file, "w") as f:
        f.write(new_text)
    # Update the module-level __version__
    global __version__
    __version__ = new_version
    return new_version

"""Adapter for backend_dev.microcli.version."""

import re
from typing import Match
from ....cli_core.version import bump_version_file, get_version

# Re-export the functions for backward compatibility

def bump_version(version_str: str) -> str:
    """
    Bump the patch version number.

    Args:
        version_str: Version string to bump.

    Returns:
        str: Bumped version string.

    Raises:
        ValueError: If the version string is not valid.
    """
    # Handle simple major.minor format (add .0 patch)
    if re.match(r'^\d+\.\d+$', version_str):
        version_str = f"{version_str}.0"

    # Validate semantic version format
    match: Match[str] = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")

    major, minor, patch = match.groups()

    # Bump patch version
    new_patch = int(patch) + 1

    return f"{major}.{minor}.{new_patch}"

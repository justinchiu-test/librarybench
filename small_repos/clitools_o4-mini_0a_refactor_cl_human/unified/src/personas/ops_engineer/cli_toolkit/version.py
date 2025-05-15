"""
Version management for the CLI Toolkit.
"""
import re
from typing import List, Optional, Tuple


def parse_version(version_str: str) -> Optional[Tuple[int, int, int]]:
    """
    Parse a version string into a tuple of (major, minor, patch).
    
    Args:
        version_str: Version string (e.g., 'v1.2.3' or '1.2.3')
        
    Returns:
        Tuple of (major, minor, patch) or None if invalid
    """
    # Strip leading 'v' if present
    if version_str.startswith('v'):
        version_str = version_str[1:]
    
    # Match semantic version pattern
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
    if not match:
        return None
    
    # Parse and return as integers
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))
    
    return major, minor, patch


def bump_version(tags: List[str]) -> str:
    """
    Bump the highest version found in a list of tags.
    
    Args:
        tags: List of version tags
        
    Returns:
        Next version string
    """
    # Default version if no valid versions found
    next_version = (0, 0, 1)
    
    # Find the highest version
    for tag in tags:
        version = parse_version(tag)
        if version is not None:
            # Compare with current highest
            if version > next_version:
                next_version = version
    
    # If a version was found, bump the patch
    if next_version > (0, 0, 1):
        major, minor, patch = next_version
        next_version = (major, minor, patch + 1)
    
    # Format as string with 'v' prefix
    return f'v{next_version[0]}.{next_version[1]}.{next_version[2]}'
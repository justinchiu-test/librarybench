"""
Version management for data scientist CLI tools.
"""

import os
import re
from typing import Optional


# Version file name
VERSION_FILE = "version.txt"


def get_version(file_path: str = VERSION_FILE) -> str:
    """
    Get version from file or default.
    
    Args:
        file_path (str, optional): Path to version file. Defaults to VERSION_FILE.
        
    Returns:
        str: Version string.
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return f.read().strip()
        else:
            return '0.0.0'
    except Exception:
        return '0.0.0'


def bump_version(file_path: str = VERSION_FILE) -> str:
    """
    Bump patch version and save to file.
    
    Args:
        file_path (str, optional): Path to version file. Defaults to VERSION_FILE.
        
    Returns:
        str: New version string.
        
    Raises:
        ValueError: If version format is invalid.
    """
    # Get current version
    current = get_version(file_path)
    
    # Parse version
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', current)
    if not match:
        raise ValueError(f"Invalid version format: {current}")
    
    major, minor, patch = match.groups()
    
    # Bump patch version
    new_version = f"{major}.{minor}.{int(patch) + 1}"
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write(new_version)
    
    return new_version
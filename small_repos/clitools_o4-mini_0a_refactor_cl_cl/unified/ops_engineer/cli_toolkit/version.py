"""
Version management for operations engineer CLI tools.
"""

import re
from typing import List, Optional


def bump_version(tags: List[str]) -> str:
    """
    Bump the version based on existing tags.
    
    Args:
        tags (List[str]): List of version tags.
        
    Returns:
        str: New version string.
    """
    # For empty list, return default version
    if not tags:
        return "v0.0.1"
    
    # Find the highest semantic version
    highest_version = (0, 0, 0)
    has_valid_tag = False
    
    for tag in tags:
        # Validate that it's a proper tag (must start with 'v')
        if not tag.startswith('v'):
            continue
            
        # Remove 'v' prefix
        tag = tag[1:]
        
        # Try to parse as semantic version
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', tag)
        if match:
            has_valid_tag = True
            major, minor, patch = match.groups()
            version = (int(major), int(minor), int(patch))
            if version > highest_version:
                highest_version = version
    
    # Return default version if no valid tags found
    if not has_valid_tag:
        return "v0.0.1"
    
    # Bump patch version
    major, minor, patch = highest_version
    return f"v{major}.{minor}.{patch + 1}"
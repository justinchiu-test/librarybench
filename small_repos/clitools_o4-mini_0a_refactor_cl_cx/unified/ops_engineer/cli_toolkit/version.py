import re

def bump_version(version_str):
    """
    Bump the patch version of a semver string
    
    Args:
        version_str: Version string in format "X.Y.Z" or "X.Y"
        
    Returns:
        str: Bumped version string
        
    Raises:
        ValueError: If version string is invalid
    """
    # Handle "X.Y" format by adding ".0"
    if re.match(r"^\d+\.\d+$", version_str):
        version_str = f"{version_str}.0"
    
    # Match "X.Y.Z" format
    pattern = r"^(\d+)\.(\d+)\.(\d+)$"
    match = re.match(pattern, version_str)
    
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
        
    major, minor, patch = map(int, match.groups())
    new_patch = patch + 1
    
    return f"{major}.{minor}.{new_patch}"
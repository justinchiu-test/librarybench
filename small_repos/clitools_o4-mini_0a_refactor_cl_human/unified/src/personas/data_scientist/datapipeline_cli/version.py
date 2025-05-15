"""
Version management for Data Pipeline CLI.
"""
import os
import re
from typing import Optional, Tuple

# The version file to use
VERSION_FILE = 'version.txt'

def get_version(package_dir: str) -> str:
    """
    Get the version from a package.
    
    Args:
        package_dir: Directory containing the package
        
    Returns:
        Version string
        
    Raises:
        ValueError: If version cannot be determined
    """
    # Try to get version from __init__.py
    init_path = os.path.join(package_dir, "__init__.py")
    if os.path.isfile(init_path):
        with open(init_path, 'r') as f:
            init_content = f.read()
            
        # Look for version string
        version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", init_content)
        if version_match:
            return version_match.group(1)
    
    # Try to get version from setup.py
    setup_path = os.path.join(package_dir, "setup.py")
    if os.path.isfile(setup_path):
        with open(setup_path, 'r') as f:
            setup_content = f.read()
            
        # Look for version string
        version_match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", setup_content)
        if version_match:
            return version_match.group(1)
    
    # Try to get version from pyproject.toml
    pyproject_path = os.path.join(package_dir, "pyproject.toml")
    if os.path.isfile(pyproject_path):
        with open(pyproject_path, 'r') as f:
            pyproject_content = f.read()
            
        # Look for version string
        version_match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", pyproject_content)
        if version_match:
            return version_match.group(1)
    
    # Version not found
    raise ValueError(f"Could not determine version for package in {package_dir}")

def update_version(package_dir: str, new_version: str, dry_run: bool = False) -> bool:
    """
    Update the version in a package.
    
    Args:
        package_dir: Directory containing the package
        new_version: New version string
        dry_run: If True, don't actually make changes
        
    Returns:
        True if version was updated
        
    Raises:
        ValueError: If version cannot be updated
    """
    updated = False
    
    # Try to update version in __init__.py
    init_path = os.path.join(package_dir, "__init__.py")
    if os.path.isfile(init_path):
        with open(init_path, 'r') as f:
            init_content = f.read()
            
        # Update version string
        new_init_content = re.sub(
            r"__version__\s*=\s*['\"]([^'\"]+)['\"]", 
            f'__version__ = "{new_version}"',
            init_content
        )
        
        # Write updated content
        if new_init_content != init_content and not dry_run:
            with open(init_path, 'w') as f:
                f.write(new_init_content)
            updated = True
    
    # Try to update version in setup.py
    setup_path = os.path.join(package_dir, "setup.py")
    if os.path.isfile(setup_path):
        with open(setup_path, 'r') as f:
            setup_content = f.read()
            
        # Update version string
        new_setup_content = re.sub(
            r"version\s*=\s*['\"]([^'\"]+)['\"]", 
            f'version="{new_version}"',
            setup_content
        )
        
        # Write updated content
        if new_setup_content != setup_content and not dry_run:
            with open(setup_path, 'w') as f:
                f.write(new_setup_content)
            updated = True
    
    # Try to update version in pyproject.toml
    pyproject_path = os.path.join(package_dir, "pyproject.toml")
    if os.path.isfile(pyproject_path):
        with open(pyproject_path, 'r') as f:
            pyproject_content = f.read()
            
        # Update version string
        new_pyproject_content = re.sub(
            r"version\s*=\s*['\"]([^'\"]+)['\"]", 
            f'version = "{new_version}"',
            pyproject_content
        )
        
        # Write updated content
        if new_pyproject_content != pyproject_content and not dry_run:
            with open(pyproject_path, 'w') as f:
                f.write(new_pyproject_content)
            updated = True
    
    return updated

def parse_version(version: str) -> Tuple[int, int, int, Optional[str]]:
    """
    Parse a semantic version string.
    
    Args:
        version: Version string (e.g., '1.2.3' or '1.2.3-beta.1')
        
    Returns:
        Tuple of (major, minor, patch, prerelease)
        
    Raises:
        ValueError: If version string is invalid
    """
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?$', version)
    if not match:
        raise ValueError(f"Invalid version string: {version}")
    
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))
    prerelease = match.group(4)
    
    return major, minor, patch, prerelease

def increment_version(version: str, part: str) -> str:
    """
    Increment a version string.
    
    Args:
        version: Version string
        part: Part to increment ('major', 'minor', or 'patch')
        
    Returns:
        Incremented version string
        
    Raises:
        ValueError: If version string or part is invalid
    """
    major, minor, patch, prerelease = parse_version(version)
    
    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    elif part == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid version part: {part}")
    
    new_version = f"{major}.{minor}.{patch}"
    if prerelease:
        new_version += f"-{prerelease}"
    
    return new_version


def get_version() -> str:
    """
    Get the current version from the version file.
    
    Returns:
        Version string
    """
    if not os.path.exists(VERSION_FILE):
        return '0.0.0'
    
    with open(VERSION_FILE, 'r') as f:
        version = f.read().strip()
    
    if not version:
        return '0.0.0'
    
    return version


def bump_version(part: str = 'patch') -> str:
    """
    Bump the version in the version file.
    
    Args:
        part: Part to increment ('major', 'minor', or 'patch')
        
    Returns:
        New version string
        
    Raises:
        ValueError: If version file contains an invalid version
    """
    current_version = get_version()
    
    try:
        new_version = increment_version(current_version, part)
    except ValueError:
        raise ValueError(f"Invalid version in {VERSION_FILE}: {current_version}")
    
    # Write new version to file
    with open(VERSION_FILE, 'w') as f:
        f.write(new_version)
    
    return new_version
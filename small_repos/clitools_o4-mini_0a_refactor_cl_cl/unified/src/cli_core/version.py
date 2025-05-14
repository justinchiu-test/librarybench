"""
Version management utilities for CLI applications.

This module provides functionality for reading, parsing, and updating version information.
"""

import os
import re
from typing import Tuple, Optional, Union


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """
    Parse a semantic version string.
    
    Args:
        version_str (str): Version string in semver format (X.Y.Z).
        
    Returns:
        Tuple[int, int, int]: (major, minor, patch) version components.
        
    Raises:
        ValueError: If the version string is not valid semver.
    """
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}. Expected X.Y.Z")
    
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def format_version(major: int, minor: int, patch: int) -> str:
    """
    Format version components as a string.
    
    Args:
        major (int): Major version number.
        minor (int): Minor version number.
        patch (int): Patch version number.
        
    Returns:
        str: Formatted version string.
    """
    return f"{major}.{minor}.{patch}"


def read_version_file(file_path: str = "version.txt") -> str:
    """
    Read version from a file.
    
    Args:
        file_path (str): Path to the version file.
        
    Returns:
        str: Version string.
        
    Raises:
        FileNotFoundError: If the version file does not exist.
    """
    with open(file_path, 'r') as f:
        return f.read().strip()


def write_version_file(version: str, file_path: str = "version.txt") -> None:
    """
    Write version to a file.
    
    Args:
        version (str): Version string to write.
        file_path (str): Path to the version file.
    """
    with open(file_path, 'w') as f:
        f.write(version)


def bump_version(current_version: str, part: str = "patch") -> str:
    """
    Bump a version component.
    
    Args:
        current_version (str): Current version string.
        part (str): Part to bump ("major", "minor", or "patch").
        
    Returns:
        str: New version string.
        
    Raises:
        ValueError: If part is not one of "major", "minor", "patch".
    """
    major, minor, patch = parse_version(current_version)
    
    if part == "major":
        return format_version(major + 1, 0, 0)
    elif part == "minor":
        return format_version(major, minor + 1, 0)
    elif part == "patch":
        return format_version(major, minor, patch + 1)
    else:
        raise ValueError(f"Invalid version part: {part}. Must be 'major', 'minor', or 'patch'")


def bump_version_file(file_path: str = "version.txt", part: str = "patch") -> str:
    """
    Read, bump, and write a version file.
    
    Args:
        file_path (str): Path to the version file.
        part (str): Part to bump ("major", "minor", or "patch").
        
    Returns:
        str: New version string.
    """
    current_version = read_version_file(file_path)
    new_version = bump_version(current_version, part)
    write_version_file(new_version, file_path)
    return new_version


def get_version(file_path: str = "version.txt", default: str = "0.1.0") -> str:
    """
    Get version from file or return default if file does not exist.
    
    Args:
        file_path (str): Path to the version file.
        default (str): Default version to return if file does not exist.
        
    Returns:
        str: Version string.
    """
    try:
        return read_version_file(file_path)
    except (FileNotFoundError, IOError):
        return default
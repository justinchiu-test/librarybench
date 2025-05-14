"""
Version management module for CLI tools.
Handles version information, bumping, and tracking.
"""

import os
import re
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


class VersionComponent(Enum):
    """Version component types for semantic versioning."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRE_RELEASE = "pre-release"
    BUILD = "build"


class Version:
    """
    Represents a semantic version.
    Follows the Semantic Versioning 2.0.0 specification (https://semver.org/).
    """
    
    def __init__(self, major: int = 0, minor: int = 1, patch: int = 0,
                pre_release: Optional[str] = None, build: Optional[str] = None):
        """
        Initialize a new version object.
        
        Args:
            major: Major version number
            minor: Minor version number
            patch: Patch version number
            pre_release: Pre-release identifier (e.g., "alpha.1", "rc.2")
            build: Build metadata (e.g., "20230304")
        """
        self.major = major
        self.minor = minor
        self.patch = patch
        self.pre_release = pre_release
        self.build = build
    
    @classmethod
    def parse(cls, version_str: str) -> 'Version':
        """
        Parse a version string into a Version object.
        
        Args:
            version_str: Version string to parse
            
        Returns:
            Version object
            
        Raises:
            ValueError: If the version string is invalid
        """
        # Regular expression for semantic version
        pattern = r'^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-.]+))?(?:\+([0-9A-Za-z-.]+))?$'
        match = re.match(pattern, version_str)
        
        if not match:
            raise ValueError(f"Invalid version string: {version_str}")
        
        major = int(match.group(1))
        minor = int(match.group(2))
        patch = int(match.group(3))
        pre_release = match.group(4)
        build = match.group(5)
        
        return cls(major, minor, patch, pre_release, build)
    
    def bump(self, component: Union[VersionComponent, str] = VersionComponent.PATCH) -> None:
        """
        Bump the version according to semantic versioning rules.
        
        Args:
            component: Component to bump
        """
        if isinstance(component, str):
            try:
                component = VersionComponent(component.lower())
            except ValueError:
                component = VersionComponent.PATCH
        
        if component == VersionComponent.MAJOR:
            self.major += 1
            self.minor = 0
            self.patch = 0
        elif component == VersionComponent.MINOR:
            self.minor += 1
            self.patch = 0
        elif component == VersionComponent.PATCH:
            self.patch += 1
        elif component == VersionComponent.PRE_RELEASE:
            # For pre-release, we just remove the pre-release tag
            self.pre_release = None
        elif component == VersionComponent.BUILD:
            # For build, we update the build metadata with a timestamp
            import datetime
            now = datetime.datetime.now()
            self.build = now.strftime("%Y%m%d%H%M%S")
        
        # When bumping version numbers, reset pre-release
        if component in (VersionComponent.MAJOR, VersionComponent.MINOR, VersionComponent.PATCH):
            self.pre_release = None
    
    def __str__(self) -> str:
        """Get the version as a string."""
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            version += f"-{self.pre_release}"
        if self.build:
            version += f"+{self.build}"
        return version
    
    def __eq__(self, other: object) -> bool:
        """Check if two versions are equal."""
        if not isinstance(other, Version):
            return NotImplemented
        
        return (self.major == other.major and
                self.minor == other.minor and
                self.patch == other.patch and
                self.pre_release == other.pre_release)
    
    def __lt__(self, other: object) -> bool:
        """Check if this version is less than another."""
        if not isinstance(other, Version):
            return NotImplemented
        
        # Compare major.minor.patch
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        
        # A version with a pre-release is less than the same version without
        if self.pre_release is None and other.pre_release is not None:
            return False
        if self.pre_release is not None and other.pre_release is None:
            return True
        
        # Compare pre-release identifiers
        if self.pre_release != other.pre_release:
            # Split by dots and compare each identifier
            self_parts = self.pre_release.split('.')
            other_parts = other.pre_release.split('.')
            
            for i in range(min(len(self_parts), len(other_parts))):
                s_part = self_parts[i]
                o_part = other_parts[i]
                
                # Numeric identifiers always have lower precedence than non-numeric
                s_is_num = s_part.isdigit()
                o_is_num = o_part.isdigit()
                
                if s_is_num and o_is_num:
                    if int(s_part) != int(o_part):
                        return int(s_part) < int(o_part)
                elif s_is_num != o_is_num:
                    return s_is_num
                elif s_part != o_part:
                    return s_part < o_part
            
            # If all identifiers are equal, the one with fewer identifiers is less
            return len(self_parts) < len(other_parts)
        
        # Build metadata does not affect precedence
        return False


class VersionManager:
    """
    Manages version information for a project.
    Handles version file discovery, parsing, and updating.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize a new version manager.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or os.getcwd()
        self.version_files: Dict[str, str] = {}
        self.current_version: Optional[Version] = None
        
        # Attempt to discover version from standard files
        self._discover_version_files()
        self._load_version()
    
    def get_version(self) -> Version:
        """
        Get the current version.
        
        Returns:
            Current version
        """
        if not self.current_version:
            self._load_version()
        
        return self.current_version or Version()
    
    def set_version(self, version: Union[Version, str]) -> None:
        """
        Set the current version.
        
        Args:
            version: New version
        """
        if isinstance(version, str):
            self.current_version = Version.parse(version)
        else:
            self.current_version = version
    
    def bump_version(self, component: Union[VersionComponent, str] = VersionComponent.PATCH) -> Version:
        """
        Bump the version according to semantic versioning rules.
        
        Args:
            component: Component to bump
            
        Returns:
            New version after bumping
        """
        version = self.get_version()
        version.bump(component)
        self.set_version(version)
        return version
    
    def save_version(self) -> bool:
        """
        Save the current version to all version files.
        
        Returns:
            True if successfully saved to at least one file
        """
        if not self.current_version:
            return False
        
        success = False
        version_str = str(self.current_version)
        
        for file_path, pattern in self.version_files.items():
            try:
                # Read file content
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Create replacement pattern
                repl = pattern.replace('VERSION', version_str)
                
                # Replace version
                updated = re.sub(pattern.replace('VERSION', r'[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z-.]+)?(?:\+[0-9A-Za-z-.]+)?'), 
                               repl, 
                               content)
                
                # Write back
                with open(file_path, 'w') as f:
                    f.write(updated)
                
                success = True
            except Exception:
                # Continue trying other files
                pass
        
        return success
    
    def _discover_version_files(self) -> None:
        """Discover version files in the project."""
        # Common version file patterns
        patterns = [
            ('setup.py', r"version\s*=\s*['\"]VERSION['\"]"),
            ('__init__.py', r"__version__\s*=\s*['\"]VERSION['\"]"),
            ('package.json', r'"version"\s*:\s*"VERSION"'),
            ('VERSION', r"VERSION"),
            ('version.txt', r"VERSION"),
            ('pyproject.toml', r"version\s*=\s*['\"]VERSION['\"]"),
        ]
        
        # Check project root first
        for filename, pattern in patterns:
            path = os.path.join(self.project_root, filename)
            if os.path.exists(path):
                self.version_files[path] = pattern
        
        # Check src directory if it exists
        src_dir = os.path.join(self.project_root, 'src')
        if os.path.exists(src_dir) and os.path.isdir(src_dir):
            for root, _, files in os.walk(src_dir):
                for file in files:
                    if file == '__init__.py' or file == 'version.py':
                        path = os.path.join(root, file)
                        self.version_files[path] = r"__version__\s*=\s*['\"]VERSION['\"]"
    
    def _load_version(self) -> None:
        """Load version from discovered files."""
        for file_path, pattern in self.version_files.items():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Extract version string using pattern
                version_pattern = pattern.replace('VERSION', r'([0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z-.]+)?(?:\+[0-9A-Za-z-.]+)?)')
                match = re.search(version_pattern, content)
                
                if match:
                    version_str = match.group(1)
                    self.current_version = Version.parse(version_str)
                    break
            except Exception:
                # Try next file
                pass
        
        # If no version found, use default
        if not self.current_version:
            self.current_version = Version()


# Create a global version manager for convenience
_global_manager = VersionManager()

def get_version() -> Version:
    """Get the current version from the global manager."""
    return _global_manager.get_version()

def set_version(version: Union[Version, str]) -> None:
    """Set the current version in the global manager."""
    _global_manager.set_version(version)

def bump_version(component: Union[VersionComponent, str] = VersionComponent.PATCH) -> Version:
    """Bump the version using the global manager."""
    return _global_manager.bump_version(component)

def save_version() -> bool:
    """Save the current version using the global manager."""
    return _global_manager.save_version()

def configure(project_root: Optional[str] = None) -> None:
    """Configure the global version manager."""
    global _global_manager
    _global_manager = VersionManager(project_root)
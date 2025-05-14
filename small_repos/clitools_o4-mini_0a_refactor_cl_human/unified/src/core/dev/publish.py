"""
Package publishing module for CLI tools.
Handles publishing packages to repositories.
"""

import os
import shutil
import subprocess
import tempfile
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple, Union


class RepositoryType(Enum):
    """Types of package repositories."""
    PYPI = "pypi"
    TESTPYPI = "testpypi"
    CUSTOM = "custom"
    LOCAL = "local"


class Publisher:
    """
    Package publisher.
    Handles building and publishing packages to repositories.
    """
    
    def __init__(self, 
                project_dir: Optional[str] = None,
                repository_type: Union[RepositoryType, str] = RepositoryType.PYPI,
                repository_url: Optional[str] = None,
                username: Optional[str] = None,
                password: Optional[str] = None,
                api_token: Optional[str] = None):
        """
        Initialize a new publisher.
        
        Args:
            project_dir: Directory containing the project
            repository_type: Type of repository to publish to
            repository_url: URL of custom repository
            username: Username for repository
            password: Password for repository
            api_token: API token for repository
        """
        self.project_dir = project_dir or os.getcwd()
        
        # Normalize repository type
        if isinstance(repository_type, str):
            try:
                self.repository_type = RepositoryType(repository_type.lower())
            except ValueError:
                self.repository_type = RepositoryType.CUSTOM
        else:
            self.repository_type = repository_type
        
        self.repository_url = repository_url
        self.username = username
        self.password = password
        self.api_token = api_token
    
    def build(self, 
             clean: bool = True, 
             build_source: bool = True, 
             build_wheel: bool = True) -> bool:
        """
        Build the package.
        
        Args:
            clean: Whether to clean previous builds
            build_source: Whether to build source distribution
            build_wheel: Whether to build wheel distribution
            
        Returns:
            True if build succeeded, False otherwise
        """
        try:
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(self.project_dir)
            
            # Clean previous builds if requested
            if clean:
                self._clean_builds()
            
            # Build package
            cmd = [sys.executable, "-m", "build"]
            
            if not build_source:
                cmd.append("--no-sdist")
            if not build_wheel:
                cmd.append("--no-wheel")
            
            subprocess.run(cmd, check=True)
            
            return True
            
        except Exception:
            return False
            
        finally:
            # Restore original directory
            os.chdir(original_dir)
    
    def publish(self, build_first: bool = True) -> bool:
        """
        Publish the package to the configured repository.
        
        Args:
            build_first: Whether to build the package first
            
        Returns:
            True if publishing succeeded, False otherwise
        """
        try:
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(self.project_dir)
            
            # Build first if requested
            if build_first and not self.build():
                return False
            
            # Prepare twine command
            cmd = ["twine", "upload"]
            
            # Add repository info
            if self.repository_type == RepositoryType.TESTPYPI:
                cmd.extend(["--repository", "testpypi"])
            elif self.repository_type == RepositoryType.CUSTOM and self.repository_url:
                cmd.extend(["--repository-url", self.repository_url])
            
            # Add credentials
            if self.api_token:
                # Use API token
                cmd.extend(["--username", "__token__", "--password", self.api_token])
            elif self.username and self.password:
                # Use username/password
                cmd.extend(["--username", self.username, "--password", self.password])
            
            # Add distribution files
            cmd.append("dist/*")
            
            # Run command
            result = subprocess.run(cmd, shell=True, check=False)
            
            return result.returncode == 0
            
        except Exception:
            return False
            
        finally:
            # Restore original directory
            os.chdir(original_dir)
    
    def publish_local(self, destination: str) -> bool:
        """
        Publish the package to a local directory.
        
        Args:
            destination: Directory to publish to
            
        Returns:
            True if publishing succeeded, False otherwise
        """
        try:
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(self.project_dir)
            
            # Build package
            if not self.build():
                return False
            
            # Create destination directory if it doesn't exist
            os.makedirs(destination, exist_ok=True)
            
            # Copy distribution files
            dist_dir = os.path.join(self.project_dir, "dist")
            for file in os.listdir(dist_dir):
                src = os.path.join(dist_dir, file)
                dst = os.path.join(destination, file)
                shutil.copy2(src, dst)
            
            return True
            
        except Exception:
            return False
            
        finally:
            # Restore original directory
            os.chdir(original_dir)
    
    def check_dependencies(self) -> List[str]:
        """
        Check if required dependencies for publishing are installed.
        
        Returns:
            List of missing dependencies
        """
        missing = []
        
        # Check if build is installed
        try:
            import build
        except ImportError:
            missing.append("build")
        
        # Check if twine is installed
        try:
            import twine
        except ImportError:
            missing.append("twine")
        
        return missing
    
    def _clean_builds(self) -> None:
        """Clean previous builds."""
        # Remove build directory
        build_dir = os.path.join(self.project_dir, "build")
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        
        # Remove dist directory
        dist_dir = os.path.join(self.project_dir, "dist")
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
        
        # Remove egg-info directories
        for item in os.listdir(self.project_dir):
            if item.endswith(".egg-info"):
                path = os.path.join(self.project_dir, item)
                if os.path.isdir(path):
                    shutil.rmtree(path)


# Import sys for executable path
import sys

# Create a global publisher for convenience
_global_publisher = Publisher()

def build(clean: bool = True, build_source: bool = True, build_wheel: bool = True) -> bool:
    """Build the package using the global publisher."""
    return _global_publisher.build(clean, build_source, build_wheel)

def publish(build_first: bool = True) -> bool:
    """Publish the package using the global publisher."""
    return _global_publisher.publish(build_first)

def publish_local(destination: str) -> bool:
    """Publish the package to a local directory using the global publisher."""
    return _global_publisher.publish_local(destination)

def check_dependencies() -> List[str]:
    """Check if required dependencies for publishing are installed."""
    return _global_publisher.check_dependencies()

def configure(project_dir: Optional[str] = None, **kwargs) -> None:
    """Configure the global publisher."""
    global _global_publisher
    _global_publisher = Publisher(project_dir, **kwargs)
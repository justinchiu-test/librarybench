"""
Package publishing utilities.

This module provides functionality for packaging and publishing CLI tools.
"""

import os
import sys
import shutil
import tempfile
import subprocess
from typing import List, Dict, Any, Optional, Union


class PackagePublisher:
    """
    Handles package building and publishing.
    
    Provides utilities for creating distribution files and uploading to PyPI.
    """
    
    def __init__(self, package_dir: str = ".", 
                build_dir: Optional[str] = None,
                repo_url: Optional[str] = None):
        """
        Initialize the package publisher.
        
        Args:
            package_dir (str): Directory containing the package to publish.
            build_dir (str, optional): Directory to use for building.
            repo_url (str, optional): URL of the package repository.
        """
        self.package_dir = os.path.abspath(package_dir)
        self.build_dir = build_dir or os.path.join(self.package_dir, "dist")
        self.repo_url = repo_url
    
    def clean_build_dir(self) -> None:
        """Clean the build directory."""
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        os.makedirs(self.build_dir, exist_ok=True)
    
    def build_sdist(self) -> List[str]:
        """
        Build a source distribution.
        
        Returns:
            List[str]: Paths to built distribution files.
        """
        self.clean_build_dir()
        
        cmd = [sys.executable, "-m", "setup", "sdist", "--dist-dir", self.build_dir]
        
        try:
            subprocess.check_call(cmd, cwd=self.package_dir)
            return [os.path.join(self.build_dir, f) for f in os.listdir(self.build_dir) 
                   if f.endswith('.tar.gz')]
        except subprocess.CalledProcessError:
            return []
    
    def build_wheel(self) -> List[str]:
        """
        Build a wheel distribution.
        
        Returns:
            List[str]: Paths to built wheel files.
        """
        self.clean_build_dir()
        
        cmd = [sys.executable, "-m", "setup", "bdist_wheel", "--dist-dir", self.build_dir]
        
        try:
            subprocess.check_call(cmd, cwd=self.package_dir)
            return [os.path.join(self.build_dir, f) for f in os.listdir(self.build_dir) 
                   if f.endswith('.whl')]
        except subprocess.CalledProcessError:
            return []
    
    def publish(self, username: Optional[str] = None, 
               password: Optional[str] = None,
               repository: Optional[str] = None) -> bool:
        """
        Publish the package to a repository.
        
        Args:
            username (str, optional): Username for authentication.
            password (str, optional): Password for authentication.
            repository (str, optional): Repository to publish to.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Build sdist and wheel
        sdist_files = self.build_sdist()
        wheel_files = self.build_wheel()
        
        if not sdist_files and not wheel_files:
            return False
        
        # Prepare twine command
        cmd = [sys.executable, "-m", "twine", "upload"]
        
        # Add repository if specified
        if repository or self.repo_url:
            cmd.extend(["--repository-url", repository or self.repo_url])
        
        # Add credentials if provided
        if username and password:
            cmd.extend(["--username", username, "--password", password])
        
        # Add distribution files
        cmd.extend(sdist_files + wheel_files)
        
        try:
            subprocess.check_call(cmd)
            return True
        except subprocess.CalledProcessError:
            return False


def build_package(package_dir: str = ".", clean: bool = True) -> List[str]:
    """
    Build a Python package.
    
    Args:
        package_dir (str): Directory containing the package.
        clean (bool): Whether to clean existing build artifacts.
        
    Returns:
        List[str]: Paths to built distribution files.
    """
    publisher = PackagePublisher(package_dir)
    
    if clean:
        publisher.clean_build_dir()
    
    sdist_files = publisher.build_sdist()
    wheel_files = publisher.build_wheel()
    
    return sdist_files + wheel_files


def publish_package(package_dir: str = ".", username: Optional[str] = None, 
                   password: Optional[str] = None, 
                   repository: Optional[str] = None) -> bool:
    """
    Build and publish a Python package.
    
    Args:
        package_dir (str): Directory containing the package.
        username (str, optional): Username for authentication.
        password (str, optional): Password for authentication.
        repository (str, optional): Repository URL.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    publisher = PackagePublisher(package_dir, repo_url=repository)
    return publisher.publish(username, password)
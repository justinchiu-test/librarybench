"""
Package publishing utilities for data scientist CLI tools.
"""

import os
import tarfile
import tempfile
from typing import Optional


def publish_package(package_dir: str) -> str:
    """
    Package a project and return the path to the resulting archive.
    
    Args:
        package_dir (str): Directory containing the project to package.
        
    Returns:
        str: Path to the created tarball.
    """
    # Create temporary file for the tar archive
    fd, temp_path = tempfile.mkstemp(suffix='.tar.gz')
    os.close(fd)
    
    # Get the directory and basename for the tar
    base_name = os.path.basename(package_dir)
    
    # Create tar archive
    with tarfile.open(temp_path, 'w:gz') as tar:
        # Add the directory to the archive
        tar.add(package_dir, arcname=base_name)
    
    return temp_path
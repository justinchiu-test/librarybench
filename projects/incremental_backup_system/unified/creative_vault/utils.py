"""
Utility functions for the CreativeVault backup system.

This module provides common utility functions used across the various
components of the CreativeVault backup system.
"""

import hashlib
import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, BinaryIO

import numpy as np
from pydantic import BaseModel


class FileInfo(BaseModel):
    """Information about a file tracked by the backup system."""
    
    path: Path
    size: int
    modified_time: float
    hash: Optional[str] = None
    content_type: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    def model_dump(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of this object
        """
        result = {
            "path": str(self.path),
            "size": self.size,
            "modified_time": self.modified_time,
            "hash": self.hash,
            "content_type": self.content_type,
            "metadata": self.metadata
        }
        return result
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for backwards compatibility).
        
        Returns:
            Dictionary representation of this object
        """
        return self.model_dump()


class BackupConfig(BaseModel):
    """Configuration for the backup system."""
    
    repository_path: Path
    compression_level: int = 6
    deduplication_enabled: bool = True
    max_delta_chain_length: int = 10
    thumbnail_size: Tuple[int, int] = (256, 256)
    max_versions_per_file: Optional[int] = None
    storage_quota: Optional[int] = None
    
    def model_dump(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation of this object
        """
        result = {
            "repository_path": str(self.repository_path),
            "compression_level": self.compression_level,
            "deduplication_enabled": self.deduplication_enabled,
            "max_delta_chain_length": self.max_delta_chain_length,
            "thumbnail_size": self.thumbnail_size,
            "max_versions_per_file": self.max_versions_per_file,
            "storage_quota": self.storage_quota
        }
        return result
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for backwards compatibility).
        
        Returns:
            Dictionary representation of this object
        """
        return self.model_dump()


def calculate_file_hash(file_path: Path, algorithm: str = 'sha256', buffer_size: int = 65536) -> str:
    """Calculate a hash for a file using the specified algorithm.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)
        buffer_size: Size of the buffer for reading the file
        
    Returns:
        String containing the hexadecimal hash
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the algorithm is not supported
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if algorithm == 'sha256':
        hasher = hashlib.sha256()
    elif algorithm == 'sha1':
        hasher = hashlib.sha1()
    elif algorithm == 'md5':
        hasher = hashlib.md5()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    with file_path.open('rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            hasher.update(data)
    
    return hasher.hexdigest()


def detect_file_type(file_path: Path) -> str:
    """Detect the type of a file based on its extension and content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        String representing the file type (e.g., "image", "model", "project")
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check by extension first
    extension = file_path.suffix.lower()
    
    # Image formats
    if extension in ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.webp']:
        return "image"
    
    # 3D model formats
    if extension in ['.obj', '.fbx', '.blend', '.3ds', '.dae', '.glb', '.gltf', '.stl', '.ply']:
        return "model"
    
    # Adobe project formats
    if extension in ['.psd', '.ai', '.indd', '.aep', '.prproj']:
        return "adobe_project"
    
    # Autodesk formats
    if extension in ['.max', '.mb', '.ma', '.c4d']:
        return "3d_project"
    
    # If we can't determine by extension, try to check content
    # This is a simplified check and would need more sophisticated logic in a real implementation
    try:
        with file_path.open('rb') as f:
            header = f.read(8)
            
            # Check for common file signatures
            if header.startswith(b'\x89PNG'):
                return "image"
            if header.startswith(b'\xff\xd8'):
                return "image"
            if header.startswith(b'BLENDER'):
                return "model"
    except Exception:
        pass
    
    # If we can't determine the type, return a generic type based on whether it's binary or text
    try:
        with file_path.open('r', encoding='utf-8') as f:
            f.read(1024)
        return "text"
    except UnicodeDecodeError:
        return "binary"


def scan_directory(directory_path: Path, include_patterns: Optional[List[str]] = None, 
                 exclude_patterns: Optional[List[str]] = None) -> List[FileInfo]:
    """Scan a directory and return information about all files.
    
    Args:
        directory_path: Path to the directory to scan
        include_patterns: Optional list of glob patterns to include
        exclude_patterns: Optional list of glob patterns to exclude
        
    Returns:
        List of FileInfo objects for all matching files
        
    Raises:
        FileNotFoundError: If the directory does not exist
    """
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    result = []
    
    # Process include and exclude patterns
    include_paths = set()
    if include_patterns:
        for pattern in include_patterns:
            include_paths.update(directory_path.glob(pattern))
    else:
        include_paths.update(directory_path.glob("**/*"))
    
    exclude_paths = set()
    if exclude_patterns:
        for pattern in exclude_patterns:
            exclude_paths.update(directory_path.glob(pattern))
    
    # Filter and create FileInfo objects
    for path in include_paths:
        if path in exclude_paths or not path.is_file():
            continue
        
        try:
            stat = path.stat()
            result.append(
                FileInfo(
                    path=path.relative_to(directory_path),
                    size=stat.st_size,
                    modified_time=stat.st_mtime,
                    content_type=detect_file_type(path)
                )
            )
        except Exception as e:
            # Log error and continue
            print(f"Error processing file {path}: {e}")
    
    return result


def create_timestamp() -> str:
    """Create a formatted timestamp for the current time.
    
    Returns:
        String containing the timestamp in the format YYYY-MM-DD_HH-MM-SS
    """
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def create_unique_id(prefix: str = "") -> str:
    """Create a unique ID string.
    
    Args:
        prefix: Optional prefix to add to the ID
        
    Returns:
        String containing a unique ID
    """
    timestamp = int(time.time() * 1000)
    random_part = np.random.randint(0, 1000000)
    return f"{prefix}{timestamp}_{random_part:06d}"


def save_json(data: Dict[str, Any], file_path: Path) -> None:
    """Save data as a JSON file.
    
    Args:
        data: Dictionary to save
        file_path: Path where the JSON file will be saved
        
    Raises:
        IOError: If the file cannot be written
    """
    # Ensure the parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with file_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=_json_serializer)


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the loaded data
        
    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    with file_path.open('r', encoding='utf-8') as f:
        return json.load(f)


def _json_serializer(obj: Any) -> Any:
    """Custom JSON serializer for types that are not JSON serializable by default.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON serializable representation of the object
        
    Raises:
        TypeError: If the object cannot be serialized
    """
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
"""
Utility functions for the unified incremental backup system.

This module provides common utility functions used across all implementations
of the incremental backup system.
"""

import hashlib
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np

def calculate_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256', buffer_size: int = 65536) -> str:
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
    file_path = Path(file_path)
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


def get_file_size(file_path: Union[str, Path]) -> int:
    """Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        int: Size of the file in bytes
    """
    return os.path.getsize(file_path)


def get_file_modification_time(file_path: Union[str, Path]) -> float:
    """Get the modification time of a file as a Unix timestamp.
    
    Args:
        file_path: Path to the file
        
    Returns:
        float: Modification time as a Unix timestamp
    """
    return os.path.getmtime(file_path)


def is_binary_file(file_path: Union[str, Path], binary_extensions: Optional[Set[str]] = None) -> bool:
    """Check if a file is binary based on its extension.
    
    Args:
        file_path: Path to the file
        binary_extensions: Set of binary file extensions
        
    Returns:
        bool: True if the file is binary, False otherwise
    """
    if binary_extensions is None:
        binary_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp',
            '.mp3', '.wav', '.ogg', '.flac', '.mp4', '.mov', '.avi',
            '.obj', '.fbx', '.blend', '.3ds', '.dae', '.glb', '.gltf',
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db',
            '.psd', '.ai', '.pdf', '.zip', '.rar', '.tar', '.gz'
        }
    
    file_path = Path(file_path)
    return file_path.suffix.lower() in binary_extensions


def detect_file_type(file_path: Union[str, Path]) -> str:
    """Detect the type of a file based on its extension and content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        String representing the file type (e.g., "image", "model", "project")
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    file_path = Path(file_path)
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
    
    # Audio formats
    if extension in ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a']:
        return "audio"
    
    # Video formats
    if extension in ['.mp4', '.mov', '.avi', '.wmv', '.mkv', '.webm']:
        return "video"
    
    # If we can't determine by extension, try to check content
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


def scan_directory(
    directory: Union[str, Path], 
    include_patterns: Optional[List[str]] = None, 
    exclude_patterns: Optional[List[str]] = None
) -> List[Path]:
    """Scan a directory recursively for files, ignoring specified patterns.
    
    Args:
        directory: Directory to scan
        include_patterns: List of glob patterns to include
        exclude_patterns: List of glob patterns to exclude
        
    Returns:
        List of paths to matching files
        
    Raises:
        FileNotFoundError: If the directory does not exist
    """
    import fnmatch
    
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    exclude_patterns = exclude_patterns or []
    result = []
    
    if include_patterns:
        # Add files matching include patterns
        for pattern in include_patterns:
            result.extend(directory.glob(pattern))
    else:
        # Walk directory structure
        for root, dirs, files in os.walk(directory):
            # Filter out directories matching exclude patterns
            dirs_to_remove = []
            for d in dirs:
                dir_path = Path(root) / d
                rel_path = dir_path.relative_to(directory)
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(str(rel_path), pattern) or fnmatch.fnmatch(d, pattern):
                        dirs_to_remove.append(d)
                        break
            
            for d in dirs_to_remove:
                dirs.remove(d)
            
            # Add files not matching exclude patterns
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(directory)
                
                skip = False
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(str(rel_path), pattern) or fnmatch.fnmatch(file, pattern):
                        skip = True
                        break
                
                if not skip:
                    result.append(file_path)
    
    return result


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


def create_timestamp() -> str:
    """Create a formatted timestamp for the current time.
    
    Returns:
        String containing the timestamp in the format YYYY-MM-DD_HH-MM-SS
    """
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def generate_timestamp() -> float:
    """Generate a current timestamp.
    
    Returns:
        float: Current Unix timestamp
    """
    return time.time()


def format_timestamp(timestamp: float) -> str:
    """Format a Unix timestamp as a human-readable string.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        str: Formatted timestamp
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def save_json(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """Save data as a JSON file.
    
    Args:
        data: Dictionary to save
        file_path: Path where the JSON file will be saved
        
    Raises:
        IOError: If the file cannot be written
    """
    file_path = Path(file_path)
    # Ensure the parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with file_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=_json_serializer)


def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the loaded data
        
    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    file_path = Path(file_path)
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
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
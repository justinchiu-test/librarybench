"""
Utility functions for GameVault.

This module contains utility functions used throughout the backup system.
"""

import hashlib
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, List, Optional, Set, Tuple, Union

import xxhash
from pyzstd import compress, decompress


def get_file_hash(file_path: Union[str, Path], chunk_size: int = 8192) -> str:
    """
    Calculate the SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read from the file
        
    Returns:
        str: Hexadecimal digest of the file hash
    """
    hasher = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError) as e:
        raise ValueError(f"Failed to calculate hash for {file_path}: {str(e)}")


def get_file_xxhash(file_path: Union[str, Path], chunk_size: int = 8192) -> str:
    """
    Calculate a faster xxHash64 hash of a file.
    
    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read from the file
        
    Returns:
        str: Hexadecimal digest of the file hash
    """
    hasher = xxhash.xxh64()
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError) as e:
        raise ValueError(f"Failed to calculate xxhash for {file_path}: {str(e)}")


def compress_data(data: bytes, level: int = 3) -> bytes:
    """
    Compress binary data using zstd.
    
    Args:
        data: Binary data to compress
        level: Compression level (0-22)
        
    Returns:
        bytes: Compressed data
    """
    return compress(data, level)


def decompress_data(compressed_data: bytes) -> bytes:
    """
    Decompress binary data using zstd.
    
    Args:
        compressed_data: Compressed binary data
        
    Returns:
        bytes: Decompressed data
    """
    return decompress(compressed_data)


def get_file_modification_time(file_path: Union[str, Path]) -> float:
    """
    Get the modification time of a file as a Unix timestamp.
    
    Args:
        file_path: Path to the file
        
    Returns:
        float: Modification time as a Unix timestamp
    """
    return os.path.getmtime(file_path)


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        int: Size of the file in bytes
    """
    return os.path.getsize(file_path)


def format_timestamp(timestamp: float) -> str:
    """
    Format a Unix timestamp as a human-readable string.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        str: Formatted timestamp
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def generate_timestamp() -> float:
    """
    Generate a current timestamp.
    
    Returns:
        float: Current Unix timestamp
    """
    return time.time()


def is_binary_file(file_path: Union[str, Path], binary_extensions: Optional[Set[str]] = None) -> bool:
    """
    Check if a file is binary based on its extension.
    
    Args:
        file_path: Path to the file
        binary_extensions: Set of binary file extensions
        
    Returns:
        bool: True if the file is binary, False otherwise
    """
    if binary_extensions is None:
        from gamevault.config import get_config
        binary_extensions = get_config().binary_extensions
    
    file_path = Path(file_path)
    return file_path.suffix.lower() in binary_extensions


def scan_directory(
    directory: Union[str, Path], 
    ignore_patterns: Optional[List[str]] = None
) -> Generator[Path, None, None]:
    """
    Scan a directory recursively for files, ignoring specified patterns.
    
    Args:
        directory: Directory to scan
        ignore_patterns: List of glob patterns to ignore
        
    Yields:
        Path: Path to each file found
    """
    if ignore_patterns is None:
        from gamevault.config import get_config
        ignore_patterns = get_config().ignore_patterns
    
    import fnmatch
    
    directory = Path(directory)
    
    for root, dirs, files in os.walk(directory):
        # Filter out directories matching ignore patterns
        dirs_to_remove = []
        for d in dirs:
            dir_path = Path(root) / d
            rel_path = dir_path.relative_to(directory)
            for pattern in ignore_patterns:
                if fnmatch.fnmatch(str(rel_path), pattern) or fnmatch.fnmatch(d, pattern):
                    dirs_to_remove.append(d)
                    break
        
        for d in dirs_to_remove:
            dirs.remove(d)
        
        # Yield files not matching ignore patterns
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(directory)
            
            skip = False
            for pattern in ignore_patterns:
                if fnmatch.fnmatch(str(rel_path), pattern) or fnmatch.fnmatch(file, pattern):
                    skip = True
                    break
            
            if not skip:
                yield file_path
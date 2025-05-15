"""
Utility functions for GameVault.

This module contains utility functions used throughout the backup system.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, List, Optional, Set, Tuple, Union

# Import common utilities from the unified library
from common.core.utils import (
    calculate_file_hash as get_file_hash,
    get_file_size,
    get_file_modification_time,
    is_binary_file,
    create_timestamp as format_timestamp,
    create_unique_id,
    generate_timestamp,
    save_json,
    load_json
)

# Import third-party libraries for compression (not included in common)
from pyzstd import compress, decompress
import xxhash


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
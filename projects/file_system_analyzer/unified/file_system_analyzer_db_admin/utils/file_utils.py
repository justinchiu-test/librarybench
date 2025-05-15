"""File system utility functions for the Database Storage Optimization Analyzer."""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Iterator, Union

# Import from common library
from common.utils.file_utils import (
    find_files as common_find_files,
    get_file_stats as common_get_file_stats,
    calculate_dir_size as common_calculate_dir_size,
    get_disk_usage as common_get_disk_usage,
    read_file_sample as common_read_file_sample,
    detect_file_type as common_detect_file_type
)


def find_files(
    root_path: Union[str, Path],
    extensions: Optional[Set[str]] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    modified_after: Optional[datetime] = None,
    modified_before: Optional[datetime] = None,
    max_depth: Optional[int] = None,
    follow_symlinks: bool = False,
    skip_hidden: bool = True,
    recursive: bool = True,
    max_files: Optional[int] = None,
) -> Iterator[Path]:
    """
    Find files matching specified criteria.

    Args:
        root_path: Starting directory for search
        extensions: File extensions to include (e.g., {'.ibd', '.myd'})
        min_size: Minimum file size in bytes
        max_size: Maximum file size in bytes
        modified_after: Only include files modified after this datetime
        modified_before: Only include files modified before this datetime
        max_depth: Maximum directory depth to search
        follow_symlinks: Whether to follow symbolic links
        skip_hidden: Whether to skip hidden files and directories
        recursive: Whether to search recursively
        max_files: Maximum number of files to return

    Returns:
        Iterator of Path objects for matching files
    """
    return common_find_files(
        root_path=root_path,
        extensions=extensions,
        min_size=min_size,
        max_size=max_size,
        modified_after=modified_after,
        modified_before=modified_before,
        max_depth=max_depth,
        follow_symlinks=follow_symlinks,
        skip_hidden=skip_hidden,
        recursive=recursive,
        max_files=max_files
    )


def get_file_stats(file_path: Union[str, Path]) -> Dict[str, Union[int, datetime, bool]]:
    """
    Get detailed file statistics.

    Args:
        file_path: Path to the file

    Returns:
        Dict containing file statistics including size, modification times, etc.
    """
    return common_get_file_stats(file_path)


def calculate_dir_size(
    dir_path: Union[str, Path], 
    follow_symlinks: bool = False,
    max_workers: int = 10
) -> int:
    """
    Calculate the total size of a directory.

    Args:
        dir_path: Path to the directory
        follow_symlinks: Whether to follow symbolic links
        max_workers: Maximum number of worker threads

    Returns:
        Total size in bytes
    """
    return common_calculate_dir_size(
        dir_path=dir_path,
        follow_symlinks=follow_symlinks,
        max_workers=max_workers
    )


def get_disk_usage(path: Union[str, Path]) -> Dict[str, Union[int, float]]:
    """
    Get disk usage statistics for the partition containing the path.

    Args:
        path: Path to check

    Returns:
        Dictionary with disk usage information
    """
    return common_get_disk_usage(path)


def read_file_sample(
    file_path: Union[str, Path], 
    max_bytes: int = 8192, 
    offset: int = 0
) -> bytes:
    """
    Read a sample of data from a file.

    Args:
        file_path: Path to the file
        max_bytes: Maximum number of bytes to read
        offset: Byte offset to start reading from

    Returns:
        Sample of file content as bytes
    """
    return common_read_file_sample(
        file_path=file_path,
        max_bytes=max_bytes,
        offset=offset
    )


def estimate_file_growth_rate(
    file_path: Union[str, Path],
    historical_sizes: List[Tuple[datetime, int]]
) -> float:
    """
    Estimate the growth rate of a file based on historical size measurements.

    Args:
        file_path: Path to the file
        historical_sizes: List of (datetime, size_bytes) tuples representing historical measurements

    Returns:
        Estimated growth rate in bytes per day
    """
    if not historical_sizes or len(historical_sizes) < 2:
        return 0.0
        
    # Sort by datetime
    sorted_sizes = sorted(historical_sizes, key=lambda x: x[0])
    
    # Calculate deltas
    deltas = []
    for i in range(1, len(sorted_sizes)):
        time_diff = (sorted_sizes[i][0] - sorted_sizes[i-1][0]).total_seconds() / 86400  # Convert to days
        if time_diff <= 0:
            continue
            
        size_diff = sorted_sizes[i][1] - sorted_sizes[i-1][1]
        growth_rate = size_diff / time_diff
        deltas.append(growth_rate)
        
    # Return average growth rate if we have data, otherwise 0
    return sum(deltas) / len(deltas) if deltas else 0.0
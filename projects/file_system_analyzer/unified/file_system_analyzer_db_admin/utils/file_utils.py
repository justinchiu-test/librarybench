"""File system utility functions for the Database Storage Optimization Analyzer."""

import os
import stat
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Iterator, Union
import platform
import psutil
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

logger = logging.getLogger(__name__)


def get_file_stats(file_path: Union[str, Path]) -> Dict[str, Union[int, datetime, bool]]:
    """
    Get detailed file statistics.

    Args:
        file_path: Path to the file

    Returns:
        Dict containing file statistics including size, modification times, etc.
    """
    try:
        path = Path(file_path)
        stats = path.stat()
        
        result = {
            "path": str(path.absolute()),
            "size_bytes": stats.st_size,
            "last_modified": datetime.fromtimestamp(stats.st_mtime),
            "creation_time": datetime.fromtimestamp(stats.st_ctime),
            "last_accessed": datetime.fromtimestamp(stats.st_atime),
            "exists": path.exists(),
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "is_symlink": path.is_symlink(),
        }
        
        # Add platform-specific information
        if platform.system() == "Windows":
            # Add Windows-specific attributes
            result["is_hidden"] = bool(stats.st_file_attributes & 0x2)  # type: ignore
            
        elif platform.system() in ["Linux", "Darwin"]:
            # Add Unix-specific attributes
            result["is_executable"] = bool(stats.st_mode & stat.S_IXUSR)
            result["permissions"] = oct(stats.st_mode & 0o777)
            
        return result
    except Exception as e:
        logger.error(f"Error getting stats for {file_path}: {str(e)}")
        return {
            "path": str(file_path),
            "exists": False,
            "error": str(e)
        }


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
    root = Path(root_path)
    if not root.exists() or not root.is_dir():
        logger.warning(f"Root path {root_path} does not exist or is not a directory")
        return

    count = 0
    
    for current_depth, (dirpath, dirnames, filenames) in enumerate(os.walk(root, followlinks=follow_symlinks)):
        # Skip hidden directories if requested
        if skip_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]

        # Respect max depth if specified
        if max_depth is not None and current_depth >= max_depth:
            dirnames.clear()  # Clear dirnames to prevent further recursion
        
        # Skip further processing if not recursive and not at root
        if not recursive and Path(dirpath) != root:
            continue

        # Process files in current directory
        for filename in filenames:
            # Skip hidden files if requested
            if skip_hidden and filename.startswith('.'):
                continue
                
            file_path = Path(dirpath) / filename
            
            # Check extension filter
            if extensions and file_path.suffix.lower() not in extensions:
                continue
                
            try:
                # Get file stats for further filtering
                stats = file_path.stat()
                
                # Size filters
                if min_size is not None and stats.st_size < min_size:
                    continue
                if max_size is not None and stats.st_size > max_size:
                    continue
                    
                # Date filters
                mod_time = datetime.fromtimestamp(stats.st_mtime)
                if modified_after is not None and mod_time < modified_after:
                    continue
                if modified_before is not None and mod_time > modified_before:
                    continue
                    
                # Yield the matching file
                yield file_path
                
                # Check if we've reached the max files limit
                count += 1
                if max_files is not None and count >= max_files:
                    return
                    
            except (PermissionError, OSError) as e:
                logger.warning(f"Error accessing {file_path}: {e}")
                continue


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
    path = Path(dir_path)
    if not path.exists() or not path.is_dir():
        return 0

    try:
        # For small directories, use a simple approach
        if len(list(path.glob('**/*'))) < 1000:
            return sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())
        
        # For larger directories, use parallel processing
        files = [f for f in path.glob('**/*') if f.is_file()]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(lambda p: p.stat().st_size, file_path) for file_path in files]
            sizes = [future.result() for future in as_completed(futures)]
            
        return sum(sizes)
    
    except (PermissionError, OSError) as e:
        logger.error(f"Error calculating size of {dir_path}: {e}")
        return 0


@lru_cache(maxsize=128)
def get_disk_usage(path: Union[str, Path]) -> Dict[str, Union[int, float]]:
    """
    Get disk usage statistics for the partition containing the path.

    Args:
        path: Path to check

    Returns:
        Dictionary with disk usage information
    """
    try:
        usage = psutil.disk_usage(str(path))
        return {
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
            "percent_used": usage.percent,
        }
    except Exception as e:
        logger.error(f"Error getting disk usage for {path}: {e}")
        return {
            "error": str(e)
        }


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
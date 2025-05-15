"""File system utility functions for file system analysis.

This module provides common utility functions for working with the file system,
including file metadata extraction, directory traversal, and file filtering.
"""

import os
import stat
import platform
import hashlib
import logging
import fnmatch
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Iterator, Union, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

from .types import FileMetadata, FileCategory


logger = logging.getLogger(__name__)


def get_file_stats(file_path: Union[str, Path]) -> Dict[str, Any]:
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
            if hasattr(stats, 'st_file_attributes'):
                result["is_hidden"] = bool(stats.st_file_attributes & 0x2)
            
        elif platform.system() in ["Linux", "Darwin"]:
            # Add Unix-specific attributes
            result["is_executable"] = bool(stats.st_mode & stat.S_IXUSR)
            result["permissions"] = oct(stats.st_mode & 0o777)
            
            # Check if hidden on Unix (starts with .)
            result["is_hidden"] = path.name.startswith('.')
            
        return result
    except Exception as e:
        logger.error(f"Error getting stats for {file_path}: {str(e)}")
        return {
            "path": str(file_path),
            "exists": False,
            "error": str(e)
        }


def create_file_metadata(file_path: Union[str, Path], 
                         calculate_hash: bool = False) -> FileMetadata:
    """
    Create a FileMetadata object from a file path.

    Args:
        file_path: Path to the file
        calculate_hash: Whether to calculate the SHA-256 hash of the file

    Returns:
        FileMetadata object with information about the file
    """
    path = Path(file_path)
    stats = get_file_stats(path)
    
    hash_sha256 = None
    if calculate_hash and stats.get("is_file", False) and stats.get("exists", False):
        try:
            hash_sha256 = calculate_file_hash(path)
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {str(e)}")
    
    # Determine basic category from file extension
    category = FileCategory.UNKNOWN
    if stats.get("is_dir", False):
        category = FileCategory.DATA
    else:
        ext = path.suffix.lower()
        if ext in {'.conf', '.cfg', '.ini', '.yaml', '.yml', '.json', '.xml', '.toml'}:
            category = FileCategory.CONFIG
        elif ext in {'.log', '.log.1', '.log.2'}:
            category = FileCategory.LOG
        elif ext in {'.bak', '.backup', '.old', '.archive'}:
            category = FileCategory.BACKUP
        elif ext in {'.tmp', '.temp'}:
            category = FileCategory.TEMP
        elif ext in {'.exe', '.dll', '.so', '.dylib', '.bin'}:
            category = FileCategory.EXECUTABLE
        elif ext in {'.doc', '.docx', '.pdf', '.txt', '.md', '.rtf'}:
            category = FileCategory.DOCUMENT
        elif ext in {'.jpg', '.jpeg', '.png', '.gif', '.mp3', '.mp4', '.wav', '.avi'}:
            category = FileCategory.MEDIA
        elif ext in {'.zip', '.tar', '.gz', '.xz', '.bz2', '.7z', '.rar'}:
            category = FileCategory.ARCHIVE
    
    return FileMetadata(
        file_path=str(path),
        file_size=stats.get("size_bytes", 0),
        creation_time=stats.get("creation_time"),
        modification_time=stats.get("last_modified", datetime.now()),
        access_time=stats.get("last_accessed"),
        owner=None,  # Would require additional system calls to retrieve owner
        permissions=stats.get("permissions"),
        hash_sha256=hash_sha256,
        is_directory=stats.get("is_dir", False),
        is_symlink=stats.get("is_symlink", False),
        is_hidden=stats.get("is_hidden", False),
        category=category
    )


def calculate_file_hash(file_path: Union[str, Path], 
                        algorithm: str = "sha256", 
                        buffer_size: int = 65536) -> str:
    """
    Calculate the hash of a file.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use ("md5", "sha1", "sha256", etc.)
        buffer_size: Size of buffer for reading file in chunks

    Returns:
        Hexadecimal hash digest of the file
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found or not a file: {file_path}")

    hash_obj = getattr(hashlib, algorithm)()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(buffer_size), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


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
    exclude_patterns: Optional[List[str]] = None,
) -> Iterator[Path]:
    """
    Find files matching specified criteria.

    Args:
        root_path: Starting directory for search
        extensions: File extensions to include (e.g., {'.txt', '.py'})
        min_size: Minimum file size in bytes
        max_size: Maximum file size in bytes
        modified_after: Only include files modified after this datetime
        modified_before: Only include files modified before this datetime
        max_depth: Maximum directory depth to search
        follow_symlinks: Whether to follow symbolic links
        skip_hidden: Whether to skip hidden files and directories
        recursive: Whether to search recursively
        max_files: Maximum number of files to return
        exclude_patterns: Glob patterns to exclude

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
                
            # Check exclude patterns
            if exclude_patterns:
                excluded = False
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(str(file_path), pattern):
                        excluded = True
                        break
                if excluded:
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
        if sum(1 for _ in path.glob('**/*')) < 1000:
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
        import psutil
        usage = psutil.disk_usage(str(path))
        return {
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
            "percent_used": usage.percent,
        }
    except ImportError:
        # Fall back to less detailed os.statvfs if psutil is not available
        try:
            if platform.system() in ["Linux", "Darwin"]:
                stats = os.statvfs(str(path))
                total = stats.f_frsize * stats.f_blocks
                free = stats.f_frsize * stats.f_bfree
                used = total - free
                return {
                    "total_bytes": total,
                    "used_bytes": used,
                    "free_bytes": free,
                    "percent_used": (used / total) * 100 if total > 0 else 0
                }
        except Exception as e:
            logger.error(f"Error getting disk usage for {path}: {e}")
    
    # If all methods fail
    return {
        "error": "Failed to get disk usage"
    }


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
    try:
        path = Path(file_path)
        
        with open(path, 'rb') as f:
            if offset > 0:
                f.seek(offset)
            return f.read(max_bytes)
            
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return b''


def detect_file_type(file_path: Union[str, Path]) -> Tuple[str, str]:
    """
    Detect the MIME type and file type of a file.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (mime_type, file_type)
    """
    import mimetypes
    
    path = Path(file_path)
    
    try:
        # Try using python-magic if available
        try:
            import magic
            mime_type = magic.from_file(str(path), mime=True)
            file_type = magic.from_file(str(path))
            return mime_type, file_type
        except ImportError:
            pass
        
        # Fall back to using file command if available
        try:
            import subprocess
            mime_type = subprocess.check_output(
                ["file", "--mime-type", "-b", str(path)], 
                universal_newlines=True
            ).strip()
            file_type = subprocess.check_output(
                ["file", "-b", str(path)], 
                universal_newlines=True
            ).strip()
            return mime_type, file_type
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # Fall back to mimetypes if all else fails
        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type is None:
            # Try to guess based on content
            with open(path, 'rb') as f:
                data = f.read(4096)
                
                # Check for common signatures
                if data.startswith(b'%PDF-'):
                    return 'application/pdf', 'PDF document'
                elif data.startswith(b'\x89PNG\r\n\x1a\n'):
                    return 'image/png', 'PNG image'
                elif data.startswith(b'\xff\xd8'):
                    return 'image/jpeg', 'JPEG image'
                elif data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
                    return 'image/gif', 'GIF image'
                elif data.startswith(b'PK\x03\x04'):
                    return 'application/zip', 'ZIP archive'
                elif data.startswith(b'\x1f\x8b'):
                    return 'application/gzip', 'GZIP archive'
                
                # Try to detect text files
                try:
                    data.decode('utf-8')
                    return 'text/plain', 'Text file'
                except UnicodeDecodeError:
                    pass
                
            mime_type = 'application/octet-stream'
            file_type = 'Binary data'
        else:
            file_type = mime_type.split('/')[-1].upper() + ' file'
            
        return mime_type, file_type
        
    except Exception as e:
        logger.error(f"Error detecting file type for {file_path}: {e}")
        return 'application/octet-stream', 'Unknown'
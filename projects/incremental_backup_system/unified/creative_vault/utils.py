"""
Utility functions for the CreativeVault backup system.

This module provides common utility functions used across the various
components of the CreativeVault backup system.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Import common utilities from the unified library
from common.core.utils import (
    calculate_file_hash, detect_file_type, scan_directory,
    create_timestamp, create_unique_id, save_json, load_json,
    get_file_size, get_file_modification_time, is_binary_file
)

# Import common models from the unified library
from common.core.models import FileInfo, BackupConfig, VersionInfo

# Re-export the imported functions and classes for backward compatibility
__all__ = [
    'FileInfo', 'BackupConfig', 'VersionInfo',
    'calculate_file_hash', 'detect_file_type', 'scan_directory',
    'create_timestamp', 'create_unique_id', 'save_json', 'load_json',
    'get_file_size', 'get_file_modification_time', 'is_binary_file'
]
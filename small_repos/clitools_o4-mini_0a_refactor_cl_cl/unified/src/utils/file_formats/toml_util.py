"""
TOML handling utilities.

This module provides functionality for reading and writing TOML files.
"""

import os
from typing import Dict, List, Any, Optional, Union

# Check if toml is available
try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False


def load_toml_file(file_path: str) -> Dict[str, Any]:
    """
    Load a TOML file.
    
    Args:
        file_path (str): Path to the TOML file.
        
    Returns:
        Dict[str, Any]: Parsed TOML data.
        
    Raises:
        ImportError: If toml is not installed.
        FileNotFoundError: If the file does not exist.
        toml.TomlDecodeError: If the file contains invalid TOML.
    """
    if not TOML_AVAILABLE:
        raise ImportError("toml is not installed. Install it with 'pip install toml'.")
    
    with open(file_path, 'r') as f:
        return toml.load(f)


def load_toml_string(content: str) -> Dict[str, Any]:
    """
    Parse a TOML string.
    
    Args:
        content (str): TOML string to parse.
        
    Returns:
        Dict[str, Any]: Parsed TOML data.
        
    Raises:
        ImportError: If toml is not installed.
        toml.TomlDecodeError: If the string contains invalid TOML.
    """
    if not TOML_AVAILABLE:
        raise ImportError("toml is not installed. Install it with 'pip install toml'.")
    
    return toml.loads(content)


def save_toml_file(data: Dict[str, Any], file_path: str) -> None:
    """
    Save data to a TOML file.
    
    Args:
        data (Dict[str, Any]): Data to save.
        file_path (str): Output file path.
        
    Raises:
        ImportError: If toml is not installed.
        IOError: If the file cannot be written.
    """
    if not TOML_AVAILABLE:
        raise ImportError("toml is not installed. Install it with 'pip install toml'.")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    with open(file_path, 'w') as f:
        toml.dump(data, f)


def to_toml_string(data: Dict[str, Any]) -> str:
    """
    Convert data to a TOML string.
    
    Args:
        data (Dict[str, Any]): Data to convert.
        
    Returns:
        str: TOML string.
        
    Raises:
        ImportError: If toml is not installed.
    """
    if not TOML_AVAILABLE:
        raise ImportError("toml is not installed. Install it with 'pip install toml'.")
    
    return toml.dumps(data)


def toml_safe_load(file_path: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Safely load a TOML file.
    
    Args:
        file_path (str): Path to the TOML file.
        default (Dict[str, Any], optional): Default to return if loading fails.
        
    Returns:
        Dict[str, Any]: Parsed TOML data or default value.
    """
    if not TOML_AVAILABLE:
        return default or {}
    
    try:
        with open(file_path, 'r') as f:
            return toml.load(f)
    except (FileNotFoundError, toml.TomlDecodeError, IOError):
        return default or {}


def toml_safe_loads(content: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Safely parse TOML content.
    
    Args:
        content (str): TOML content to parse.
        default (Dict[str, Any], optional): Default to return if parsing fails.
        
    Returns:
        Dict[str, Any]: Parsed TOML data or default value.
    """
    if not TOML_AVAILABLE:
        return default or {}
    
    try:
        return toml.loads(content)
    except toml.TomlDecodeError:
        return default or {}
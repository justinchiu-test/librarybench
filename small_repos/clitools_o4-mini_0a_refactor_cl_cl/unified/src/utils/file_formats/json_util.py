"""
JSON handling utilities.

This module provides functionality for reading and writing JSON files.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load a JSON file.
    
    Args:
        file_path (str): Path to the JSON file.
        
    Returns:
        Dict[str, Any]: Parsed JSON data.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def load_json_string(content: str) -> Dict[str, Any]:
    """
    Parse a JSON string.
    
    Args:
        content (str): JSON string to parse.
        
    Returns:
        Dict[str, Any]: Parsed JSON data.
        
    Raises:
        json.JSONDecodeError: If the string contains invalid JSON.
    """
    return json.loads(content)


def save_json_file(data: Dict[str, Any], file_path: str, indent: int = 2) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data (Dict[str, Any]): Data to save.
        file_path (str): Output file path.
        indent (int): Indentation level for pretty printing.
        
    Raises:
        IOError: If the file cannot be written.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent)


def to_json_string(data: Dict[str, Any], indent: Optional[int] = None) -> str:
    """
    Convert data to a JSON string.
    
    Args:
        data (Dict[str, Any]): Data to convert.
        indent (int, optional): Indentation level for pretty printing.
        
    Returns:
        str: JSON string.
    """
    return json.dumps(data, indent=indent)


def json_safe_loads(content: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Safely parse JSON content.
    
    Args:
        content (str): JSON content to parse.
        default (Dict[str, Any], optional): Default to return if parsing fails.
        
    Returns:
        Dict[str, Any]: Parsed JSON data or default value.
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return default or {}


def json_safe_load(file_path: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Safely load a JSON file.
    
    Args:
        file_path (str): Path to the JSON file.
        default (Dict[str, Any], optional): Default to return if loading fails.
        
    Returns:
        Dict[str, Any]: Parsed JSON data or default value.
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        return default or {}
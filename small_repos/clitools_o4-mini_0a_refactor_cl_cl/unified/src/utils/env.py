"""
Environment utilities for CLI applications.

This module provides functionality for interacting with environment variables.
"""

import os
import json
from typing import Dict, Any, Optional, Union, List


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an environment variable value.
    
    Args:
        key (str): Environment variable key.
        default (str, optional): Default value if not found.
        
    Returns:
        str or None: Environment variable value or default.
    """
    return os.environ.get(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """
    Get a boolean environment variable value.
    
    True values: "1", "true", "yes", "y", "on" (case-insensitive)
    False values: all other values
    
    Args:
        key (str): Environment variable key.
        default (bool): Default value if not found.
        
    Returns:
        bool: Boolean value of the environment variable.
    """
    value = get_env(key)
    
    if value is None:
        return default
    
    return value.lower() in ("1", "true", "yes", "y", "on")


def get_env_int(key: str, default: Optional[int] = None) -> Optional[int]:
    """
    Get an integer environment variable value.
    
    Args:
        key (str): Environment variable key.
        default (int, optional): Default value if not found or not an integer.
        
    Returns:
        int or None: Integer value of the environment variable or default.
    """
    value = get_env(key)
    
    if value is None:
        return default
    
    try:
        return int(value)
    except ValueError:
        return default


def get_env_float(key: str, default: Optional[float] = None) -> Optional[float]:
    """
    Get a float environment variable value.
    
    Args:
        key (str): Environment variable key.
        default (float, optional): Default value if not found or not a float.
        
    Returns:
        float or None: Float value of the environment variable or default.
    """
    value = get_env(key)
    
    if value is None:
        return default
    
    try:
        return float(value)
    except ValueError:
        return default


def get_env_list(key: str, default: Optional[List[str]] = None, 
                delimiter: str = ",") -> Optional[List[str]]:
    """
    Get a list from an environment variable.
    
    Args:
        key (str): Environment variable key.
        default (List[str], optional): Default value if not found.
        delimiter (str): Delimiter for splitting the list.
        
    Returns:
        List[str] or None: List from the environment variable or default.
    """
    value = get_env(key)
    
    if value is None:
        return default or []
    
    return [item.strip() for item in value.split(delimiter)]


def get_env_dict(key: str, default: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Get a dictionary from a JSON environment variable.
    
    Args:
        key (str): Environment variable key.
        default (Dict[str, Any], optional): Default value if not found or not valid JSON.
        
    Returns:
        Dict[str, Any] or None: Dictionary from the environment variable or default.
    """
    value = get_env(key)
    
    if value is None:
        return default or {}
    
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default or {}


def set_env(key: str, value: Union[str, int, float, bool]) -> None:
    """
    Set an environment variable.
    
    Args:
        key (str): Environment variable key.
        value (Union[str, int, float, bool]): Value to set.
    """
    os.environ[key] = str(value)


def set_env_dict(key: str, value: Dict[str, Any]) -> None:
    """
    Set a dictionary as a JSON environment variable.
    
    Args:
        key (str): Environment variable key.
        value (Dict[str, Any]): Dictionary to set.
    """
    os.environ[key] = json.dumps(value)


def clear_env(key: str) -> None:
    """
    Remove an environment variable.
    
    Args:
        key (str): Environment variable key.
    """
    if key in os.environ:
        del os.environ[key]


def get_env_prefix(prefix: str) -> Dict[str, str]:
    """
    Get all environment variables with a specific prefix.
    
    Args:
        prefix (str): Prefix to filter by.
        
    Returns:
        Dict[str, str]: Dictionary of environment variables with the prefix.
    """
    return {key: value for key, value in os.environ.items() if key.startswith(prefix)}
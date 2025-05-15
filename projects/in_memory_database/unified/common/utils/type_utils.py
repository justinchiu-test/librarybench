"""
Type conversion and handling utilities.

This module provides functions for converting between different data types
and checking type properties.
"""

from typing import Any, Optional, Type, TypeVar, Union, List, Dict, Set, Tuple, Callable

T = TypeVar('T')


def to_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """
    Convert a value to an integer, returning a default if conversion fails.
    
    Args:
        value: The value to convert.
        default: Default value to return if conversion fails.
    
    Returns:
        The converted integer, or default if conversion fails.
    """
    if value is None:
        return default
    
    try:
        if isinstance(value, bool):
            return int(value)
        elif isinstance(value, (int, float)):
            return int(value)
        elif isinstance(value, str) and value.strip():
            # Handle strings like "123", "123.45"
            return int(float(value))
        else:
            return default
    except (ValueError, TypeError):
        return default


def to_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    """
    Convert a value to a float, returning a default if conversion fails.
    
    Args:
        value: The value to convert.
        default: Default value to return if conversion fails.
    
    Returns:
        The converted float, or default if conversion fails.
    """
    if value is None:
        return default
    
    try:
        if isinstance(value, bool):
            return float(value)
        elif isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str) and value.strip():
            return float(value)
        else:
            return default
    except (ValueError, TypeError):
        return default


def to_bool(value: Any, default: Optional[bool] = None) -> Optional[bool]:
    """
    Convert a value to a boolean, returning a default if conversion fails.
    
    Args:
        value: The value to convert.
        default: Default value to return if conversion fails.
    
    Returns:
        The converted boolean, or default if conversion fails.
    """
    if value is None:
        return default
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    if isinstance(value, str):
        value = value.lower().strip()
        if value in ('true', 'yes', 'y', '1'):
            return True
        elif value in ('false', 'no', 'n', '0'):
            return False
    
    return default


def to_string(value: Any, default: Optional[str] = None) -> Optional[str]:
    """
    Convert a value to a string, returning a default if conversion fails.
    
    Args:
        value: The value to convert.
        default: Default value to return if conversion fails.
    
    Returns:
        The converted string, or default if conversion fails.
    """
    if value is None:
        return default
    
    try:
        return str(value)
    except (ValueError, TypeError):
        return default


def safe_cast(value: Any, target_type: Type[T], default: Optional[T] = None) -> Optional[T]:
    """
    Safely cast a value to a target type, returning a default if casting fails.
    
    Args:
        value: The value to cast.
        target_type: The type to cast to.
        default: Default value to return if casting fails.
    
    Returns:
        The casted value, or default if casting fails.
    """
    if value is None:
        return default
    
    try:
        if target_type is bool:
            return to_bool(value, default)
        elif target_type is int:
            return to_int(value, default)
        elif target_type is float:
            return to_float(value, default)
        elif target_type is str:
            return to_string(value, default)
        else:
            return target_type(value)
    except (ValueError, TypeError):
        return default


def is_numeric(value: Any) -> bool:
    """
    Check if a value is numeric (int or float but not bool).
    
    Args:
        value: The value to check.
    
    Returns:
        True if the value is numeric, False otherwise.
    """
    if isinstance(value, bool):
        return False
    
    if isinstance(value, (int, float)):
        return True
    
    if isinstance(value, str):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    return False


def is_collection(value: Any) -> bool:
    """
    Check if a value is a collection (list, tuple, set, dict).
    
    Args:
        value: The value to check.
    
    Returns:
        True if the value is a collection, False otherwise.
    """
    return isinstance(value, (list, tuple, set, dict))


def get_nested_value(
    data: Dict[str, Any],
    path: str,
    default: Any = None,
    separator: str = "."
) -> Any:
    """
    Get a value from a nested dictionary using a path string.
    
    Args:
        data: The dictionary to get the value from.
        path: The path to the value, using a separator to indicate nesting.
        default: Default value to return if the path doesn't exist.
        separator: The character used to separate path components.
    
    Returns:
        The value at the specified path, or default if the path doesn't exist.
    """
    parts = path.split(separator)
    current = data
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    
    return current


def set_nested_value(
    data: Dict[str, Any],
    path: str,
    value: Any,
    separator: str = ".",
    create_path: bool = True
) -> None:
    """
    Set a value in a nested dictionary using a path string.
    
    Args:
        data: The dictionary to set the value in.
        path: The path to the value, using a separator to indicate nesting.
        value: The value to set.
        separator: The character used to separate path components.
        create_path: Whether to create the path if it doesn't exist.
    
    Raises:
        KeyError: If a part of the path doesn't exist and create_path is False.
    """
    parts = path.split(separator)
    current = data
    
    for i, part in enumerate(parts[:-1]):
        if part not in current:
            if create_path:
                current[part] = {}
            else:
                raise KeyError(f"Path component '{part}' not found")
        
        current = current[part]
        
        if not isinstance(current, dict):
            if create_path:
                # Convert to dict if not already
                current = {}
                data[part] = current
            else:
                raise KeyError(
                    f"Path component '{part}' refers to a non-dictionary value"
                )
    
    current[parts[-1]] = value
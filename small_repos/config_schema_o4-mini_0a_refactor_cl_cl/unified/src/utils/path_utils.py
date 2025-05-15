"""Path utilities for dot notation access to nested dictionaries."""
from typing import Dict, Any, Optional, List, Tuple, Union


class DotNotationAccess:
    """Utility class for accessing nested dictionaries with dot notation."""
    
    @classmethod
    def get(cls, data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """Get a value from a nested dictionary using dot notation.
        
        Args:
            data: The dictionary to get a value from
            path: The path to the value using dot notation
            default: The default value to return if the path is not found
            
        Returns:
            The value at the specified path, or the default value if not found
            
        Raises:
            KeyError: If the path is not found and no default value is provided
        """
        if not path:
            return data
            
        parts = path.split('.')
        current = data
        
        for i, part in enumerate(parts):
            if not isinstance(current, dict):
                if default is not None:
                    return default
                raise KeyError(f"Cannot access '{part}' in '{'.'.join(parts[:i])}': not a dictionary")
                
            if part not in current:
                if default is not None:
                    return default
                raise KeyError(f"Path '{path}' not found in configuration")
                
            current = current[part]
            
        return current
    
    @classmethod
    def set(cls, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set a value in a nested dictionary using dot notation.
        
        Args:
            data: The dictionary to set a value in
            path: The path to the value using dot notation
            value: The value to set
        """
        if not path:
            raise ValueError("Path cannot be empty")
            
        parts = path.split('.')
        current = data
        
        for i, part in enumerate(parts[:-1]):
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
            
        current[parts[-1]] = value


def get_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get a value from a nested dictionary using dot notation.
    
    Args:
        data: The dictionary to get a value from
        path: The path to the value using dot notation
        default: The default value to return if the path is not found
        
    Returns:
        The value at the specified path, or the default value if not found
        
    Raises:
        KeyError: If the path is not found and no default value is provided
    """
    return DotNotationAccess.get(data, path, default)


def set_value(data: Dict[str, Any], path: str, value: Any) -> None:
    """Set a value in a nested dictionary using dot notation.
    
    Args:
        data: The dictionary to set a value in
        path: The path to the value using dot notation
        value: The value to set
    """
    DotNotationAccess.set(data, path, value)
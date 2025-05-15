"""Type conversion utilities for configuration values."""
import re
from typing import Any, Type, Dict, List, Union, Optional, Callable, TypeVar, cast

T = TypeVar('T')


class TypeConverter:
    """Utility class for type conversion and inference."""
    
    @classmethod
    def convert_value(cls, value: Any, target_type: Type[T]) -> T:
        """Convert a value to a specified type.
        
        Args:
            value: The value to convert
            target_type: The target type to convert to
            
        Returns:
            The converted value
            
        Raises:
            ValueError: If the value cannot be converted to the target type
        """
        if isinstance(value, target_type):
            return value
            
        if target_type == bool and isinstance(value, str):
            return cls._str_to_bool(value)
            
        if target_type == list and isinstance(value, str):
            return cls._str_to_list(value)
            
        if target_type == int and isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to int")
                
        if target_type == float and isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to float")
                
        # Default conversion attempt
        try:
            return target_type(value)
        except (ValueError, TypeError):
            raise ValueError(f"Cannot convert '{value}' (type {type(value).__name__}) to {target_type.__name__}")
    
    @classmethod
    def infer_type(cls, value: Any) -> Type:
        """Infer the type of a value.
        
        Args:
            value: The value to infer the type of
            
        Returns:
            The inferred type
        """
        if value is None:
            return type(None)
        return type(value)
    
    @classmethod
    def _str_to_bool(cls, value: str) -> bool:
        """Convert a string to a boolean.
        
        Args:
            value: The string to convert
            
        Returns:
            The boolean value
            
        Raises:
            ValueError: If the string cannot be converted to a boolean
        """
        value = value.lower()
        if value in ('true', 'yes', 'y', '1', 'on'):
            return True
        if value in ('false', 'no', 'n', '0', 'off'):
            return False
        raise ValueError(f"Cannot convert '{value}' to boolean")
    
    @classmethod
    def _str_to_list(cls, value: str) -> List[str]:
        """Convert a comma-separated string to a list.
        
        Args:
            value: The string to convert
            
        Returns:
            The list of values
        """
        if not value:
            return []
        return [item.strip() for item in value.split(',')]


def convert_value(value: Any, target_type: Type[T]) -> T:
    """Convert a value to a specified type.
    
    Args:
        value: The value to convert
        target_type: The target type to convert to
        
    Returns:
        The converted value
        
    Raises:
        ValueError: If the value cannot be converted to the target type
    """
    return TypeConverter.convert_value(value, target_type)


def infer_type(value: Any) -> Type:
    """Infer the type of a value.
    
    Args:
        value: The value to infer the type of
        
    Returns:
        The inferred type
    """
    return TypeConverter.infer_type(value)
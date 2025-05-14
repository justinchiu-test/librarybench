"""
Validation utilities for CLI applications.

This module provides functionality for validating configuration and user input.
"""

import re
from typing import Dict, List, Any, Optional, Union, Callable, Type


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


def validate_type(value: Any, expected_type: Type) -> bool:
    """
    Validate that a value is of the expected type.
    
    Args:
        value: Value to validate.
        expected_type: Expected type.
        
    Returns:
        bool: True if value is of the expected type, False otherwise.
    """
    return isinstance(value, expected_type)


def validate_pattern(value: str, pattern: str) -> bool:
    """
    Validate that a string matches a regular expression pattern.
    
    Args:
        value (str): String to validate.
        pattern (str): Regular expression pattern.
        
    Returns:
        bool: True if the string matches the pattern, False otherwise.
    """
    return bool(re.match(pattern, value))


def validate_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                 max_value: Optional[Union[int, float]] = None) -> bool:
    """
    Validate that a number is within a specified range.
    
    Args:
        value (Union[int, float]): Number to validate.
        min_value (Union[int, float], optional): Minimum allowed value (inclusive).
        max_value (Union[int, float], optional): Maximum allowed value (inclusive).
        
    Returns:
        bool: True if the number is within the range, False otherwise.
    """
    if min_value is not None and value < min_value:
        return False
    
    if max_value is not None and value > max_value:
        return False
    
    return True


def validate_length(value: Union[str, List, Dict], min_length: Optional[int] = None, 
                  max_length: Optional[int] = None) -> bool:
    """
    Validate that a string or collection is within a specified length range.
    
    Args:
        value (Union[str, List, Dict]): Value to validate.
        min_length (int, optional): Minimum allowed length (inclusive).
        max_length (int, optional): Maximum allowed length (inclusive).
        
    Returns:
        bool: True if the value's length is within the range, False otherwise.
    """
    length = len(value)
    
    if min_length is not None and length < min_length:
        return False
    
    if max_length is not None and length > max_length:
        return False
    
    return True


def validate_one_of(value: Any, valid_values: List[Any]) -> bool:
    """
    Validate that a value is one of a set of valid values.
    
    Args:
        value: Value to validate.
        valid_values (List[Any]): List of valid values.
        
    Returns:
        bool: True if the value is in the list of valid values, False otherwise.
    """
    return value in valid_values


def validate_dict_schema(data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Validate a dictionary against a schema.
    
    Args:
        data (Dict[str, Any]): Dictionary to validate.
        schema (Dict[str, Dict[str, Any]]): Schema defining validation rules.
        
    Returns:
        Dict[str, List[str]]: Dictionary mapping field names to validation errors.
    """
    errors = {}
    
    # Check required fields
    for field_name, field_schema in schema.items():
        if field_schema.get('required', False) and field_name not in data:
            errors[field_name] = [f"Field '{field_name}' is required"]
    
    # Validate fields
    for field_name, value in data.items():
        field_errors = []
        
        if field_name in schema:
            field_schema = schema[field_name]
            
            # Type validation
            if 'type' in field_schema:
                expected_type = field_schema['type']
                if not isinstance(value, expected_type):
                    field_errors.append(f"Expected type {expected_type.__name__}, got {type(value).__name__}")
            
            # Pattern validation
            if 'pattern' in field_schema and isinstance(value, str):
                pattern = field_schema['pattern']
                if not validate_pattern(value, pattern):
                    field_errors.append(f"Value does not match pattern: {pattern}")
            
            # Range validation
            if ('min_value' in field_schema or 'max_value' in field_schema) and isinstance(value, (int, float)):
                min_value = field_schema.get('min_value')
                max_value = field_schema.get('max_value')
                if not validate_range(value, min_value, max_value):
                    range_str = ""
                    if min_value is not None:
                        range_str += f">= {min_value}"
                    if max_value is not None:
                        if range_str:
                            range_str += " and "
                        range_str += f"<= {max_value}"
                    field_errors.append(f"Value must be {range_str}")
            
            # Length validation
            if ('min_length' in field_schema or 'max_length' in field_schema) and hasattr(value, '__len__'):
                min_length = field_schema.get('min_length')
                max_length = field_schema.get('max_length')
                if not validate_length(value, min_length, max_length):
                    length_str = ""
                    if min_length is not None:
                        length_str += f">= {min_length}"
                    if max_length is not None:
                        if length_str:
                            length_str += " and "
                        length_str += f"<= {max_length}"
                    field_errors.append(f"Length must be {length_str}")
            
            # Enum validation
            if 'enum' in field_schema:
                enum_values = field_schema['enum']
                if not validate_one_of(value, enum_values):
                    field_errors.append(f"Value must be one of: {', '.join(str(v) for v in enum_values)}")
            
            # Custom validation
            if 'validator' in field_schema and callable(field_schema['validator']):
                validator = field_schema['validator']
                try:
                    if not validator(value):
                        field_errors.append("Value failed custom validation")
                except Exception as e:
                    field_errors.append(f"Validation error: {str(e)}")
        
        if field_errors:
            errors[field_name] = field_errors
    
    return errors


def validate_config(config: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> None:
    """
    Validate a configuration dictionary against a schema.
    
    Args:
        config (Dict[str, Any]): Configuration to validate.
        schema (Dict[str, Dict[str, Any]]): Schema defining validation rules.
        
    Raises:
        ValidationError: If validation fails.
    """
    errors = validate_dict_schema(config, schema)
    
    if errors:
        error_message = "Configuration validation failed:"
        for field, field_errors in errors.items():
            error_message += f"\n  {field}: {'; '.join(field_errors)}"
        raise ValidationError(error_message)
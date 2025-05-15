"""Validation utilities shared across implementations."""

import re
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Pattern, Set, Type, TypeVar, Union, cast

from pydantic import BaseModel, validator

T = TypeVar('T')


def validate_non_negative(value: Union[int, float, Decimal]) -> Union[int, float, Decimal]:
    """
    Validate that a value is non-negative.
    
    Args:
        value: Value to validate
        
    Returns:
        The value if valid
        
    Raises:
        ValueError: If the value is negative
    """
    if value < 0:
        raise ValueError("Value must be non-negative")
    return value


def validate_positive(value: Union[int, float, Decimal]) -> Union[int, float, Decimal]:
    """
    Validate that a value is positive.
    
    Args:
        value: Value to validate
        
    Returns:
        The value if valid
        
    Raises:
        ValueError: If the value is not positive
    """
    if value <= 0:
        raise ValueError("Value must be positive")
    return value


def validate_percentage(value: Union[int, float, Decimal]) -> Union[int, float, Decimal]:
    """
    Validate that a value is a percentage (0-100).
    
    Args:
        value: Value to validate
        
    Returns:
        The value if valid
        
    Raises:
        ValueError: If the value is not between 0 and 100
    """
    if value < 0 or value > 100:
        raise ValueError("Value must be between 0 and 100")
    return value


def validate_decimal_percentage(value: Union[float, Decimal]) -> Union[float, Decimal]:
    """
    Validate that a value is a decimal percentage (0-1).
    
    Args:
        value: Value to validate
        
    Returns:
        The value if valid
        
    Raises:
        ValueError: If the value is not between 0 and 1
    """
    if value < 0 or value > 1:
        raise ValueError("Value must be between 0 and 1")
    return value


def validate_date_not_future(value: Union[date, datetime]) -> Union[date, datetime]:
    """
    Validate that a date is not in the future.
    
    Args:
        value: Date to validate
        
    Returns:
        The date if valid
        
    Raises:
        ValueError: If the date is in the future
    """
    # Get current date
    current = datetime.now().date() if isinstance(value, date) else datetime.now()
    
    if value > current:
        raise ValueError("Date cannot be in the future")
    return value


def validate_date_range(
    start: Union[date, datetime], end: Union[date, datetime]
) -> Tuple[Union[date, datetime], Union[date, datetime]]:
    """
    Validate that a date range is valid (start <= end).
    
    Args:
        start: Start date
        end: End date
        
    Returns:
        Tuple of (start, end) if valid
        
    Raises:
        ValueError: If the start date is after the end date
    """
    if start > end:
        raise ValueError("Start date cannot be after end date")
    return start, end


def validate_string_not_empty(value: str) -> str:
    """
    Validate that a string is not empty.
    
    Args:
        value: String to validate
        
    Returns:
        The string if valid
        
    Raises:
        ValueError: If the string is empty
    """
    if not value:
        raise ValueError("String cannot be empty")
    return value


def validate_string_length(
    value: str, min_length: int = 0, max_length: Optional[int] = None
) -> str:
    """
    Validate that a string is within length constraints.
    
    Args:
        value: String to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length (None for no upper limit)
        
    Returns:
        The string if valid
        
    Raises:
        ValueError: If the string length is outside the allowed range
    """
    if len(value) < min_length:
        raise ValueError(f"String must be at least {min_length} characters long")
    
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"String cannot be longer than {max_length} characters")
    
    return value


def validate_string_pattern(value: str, pattern: Union[str, Pattern]) -> str:
    """
    Validate that a string matches a pattern.
    
    Args:
        value: String to validate
        pattern: Regex pattern to match
        
    Returns:
        The string if valid
        
    Raises:
        ValueError: If the string doesn't match the pattern
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    
    if not pattern.match(value):
        raise ValueError("String does not match the required pattern")
    
    return value


def validate_email(value: str) -> str:
    """
    Validate that a string is a valid email address.
    
    Args:
        value: Email to validate
        
    Returns:
        The email if valid
        
    Raises:
        ValueError: If the email is invalid
    """
    # Simple regex for email validation
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    if not re.match(email_pattern, value):
        raise ValueError("Invalid email address")
    
    return value


def validate_in_set(value: Any, allowed_values: Set[Any]) -> Any:
    """
    Validate that a value is in a set of allowed values.
    
    Args:
        value: Value to validate
        allowed_values: Set of allowed values
        
    Returns:
        The value if valid
        
    Raises:
        ValueError: If the value is not in the allowed set
    """
    if value not in allowed_values:
        values_str = ", ".join(str(v) for v in allowed_values)
        raise ValueError(f"Value must be one of: {values_str}")
    
    return value


def validate_list_not_empty(value: List[Any]) -> List[Any]:
    """
    Validate that a list is not empty.
    
    Args:
        value: List to validate
        
    Returns:
        The list if valid
        
    Raises:
        ValueError: If the list is empty
    """
    if not value:
        raise ValueError("List cannot be empty")
    
    return value


def validate_list_length(
    value: List[Any], min_length: int = 0, max_length: Optional[int] = None
) -> List[Any]:
    """
    Validate that a list is within length constraints.
    
    Args:
        value: List to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length (None for no upper limit)
        
    Returns:
        The list if valid
        
    Raises:
        ValueError: If the list length is outside the allowed range
    """
    if len(value) < min_length:
        raise ValueError(f"List must have at least {min_length} items")
    
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"List cannot have more than {max_length} items")
    
    return value


def add_validator(
    model_class: Type[BaseModel], field_name: str, validator_func: Callable, **kwargs: Any
) -> Type[BaseModel]:
    """
    Dynamically add a validator to a Pydantic model.
    
    Args:
        model_class: The Pydantic model class
        field_name: The field to validate
        validator_func: The validator function
        **kwargs: Additional validator parameters
        
    Returns:
        Updated model class
    """
    # Create a named validator
    validator_name = f"validate_{field_name}_{validator_func.__name__}"
    
    # Create the validator function
    def dynamic_validator(cls, v, values):
        return validator_func(v)
    
    # Set the function name
    dynamic_validator.__name__ = validator_name
    
    # Add the validator to the model
    validator_decorator = validator(field_name, **kwargs)
    model_class = type(
        model_class.__name__,
        (model_class,),
        {validator_name: validator_decorator(dynamic_validator)},
    )
    
    return cast(Type[BaseModel], model_class)
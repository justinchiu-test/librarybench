"""Input validation for query language interpreters."""

import re
from typing import Any, Dict, List, Optional, Pattern, Set, Union, TypeVar, Callable

T = TypeVar("T")


def validate_input(
    value: Any,
    validator: Callable[[Any], bool],
    error_message: str = "Invalid input",
) -> None:
    """Validate input value.

    Args:
        value: Value to validate
        validator: Validation function
        error_message: Error message if validation fails

    Raises:
        ValueError: If validation fails
    """
    if not validator(value):
        raise ValueError(error_message)


def validate_type(value: Any, expected_type: type) -> bool:
    """Validate that a value is of the expected type.

    Args:
        value: Value to validate
        expected_type: Expected type

    Returns:
        bool: True if valid, False otherwise
    """
    return isinstance(value, expected_type)


def validate_string(
    value: str,
    min_length: int = 0,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
) -> bool:
    """Validate a string value.

    Args:
        value: String to validate
        min_length: Minimum length
        max_length: Maximum length (None for no limit)
        pattern: Regex pattern to match (None for no pattern check)

    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(value, str):
        return False

    if len(value) < min_length:
        return False

    if max_length is not None and len(value) > max_length:
        return False

    if pattern is not None and not re.match(pattern, value):
        return False

    return True


def validate_number(
    value: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    allow_float: bool = True,
) -> bool:
    """Validate a numeric value.

    Args:
        value: Number to validate
        min_value: Minimum value (None for no minimum)
        max_value: Maximum value (None for no maximum)
        allow_float: Whether to allow float values

    Returns:
        bool: True if valid, False otherwise
    """
    if isinstance(value, int):
        pass  # Integers are always allowed
    elif isinstance(value, float) and allow_float:
        pass  # Floats are allowed if allow_float is True
    else:
        return False

    if min_value is not None and value < min_value:
        return False

    if max_value is not None and value > max_value:
        return False

    return True


def validate_list(
    value: List[Any],
    min_length: int = 0,
    max_length: Optional[int] = None,
    item_validator: Optional[Callable[[Any], bool]] = None,
) -> bool:
    """Validate a list value.

    Args:
        value: List to validate
        min_length: Minimum length
        max_length: Maximum length (None for no limit)
        item_validator: Validator for list items (None for no item validation)

    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(value, list):
        return False

    if len(value) < min_length:
        return False

    if max_length is not None and len(value) > max_length:
        return False

    if item_validator is not None:
        return all(item_validator(item) for item in value)

    return True


def validate_dict(
    value: Dict[str, Any],
    required_keys: Set[str] = None,
    optional_keys: Set[str] = None,
    key_validators: Dict[str, Callable[[Any], bool]] = None,
) -> bool:
    """Validate a dictionary value.

    Args:
        value: Dictionary to validate
        required_keys: Required keys (None for no required keys)
        optional_keys: Optional keys (None for any keys allowed)
        key_validators: Validators for specific keys (None for no key validation)

    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(value, dict):
        return False

    # Check required keys
    if required_keys is not None:
        if not required_keys.issubset(set(value.keys())):
            return False

    # Check that all keys are either required or optional
    if required_keys is not None and optional_keys is not None:
        allowed_keys = required_keys.union(optional_keys)
        if not set(value.keys()).issubset(allowed_keys):
            return False

    # Validate specific keys
    if key_validators is not None:
        for key, validator in key_validators.items():
            if key in value and not validator(value[key]):
                return False

    return True

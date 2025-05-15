"""
Data validation utilities.

This module provides functions for validating data against expected types
and constraints.
"""

from typing import Any, Dict, List, Optional, Type, Union, Callable, Tuple
import re


def validate_type(
    value: Any,
    expected_type: Union[Type, Tuple[Type, ...], str],
    field_name: str = "Value"
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is of an expected type.
    
    Args:
        value: The value to validate.
        expected_type: The expected type or types.
        field_name: Name of the field being validated (for error messages).
    
    Returns:
        A tuple containing a boolean indicating whether the value is valid,
        and an optional error message if it's not.
    """
    if value is None:
        return True, None
    
    if isinstance(expected_type, str):
        if expected_type == "any":
            return True, None
        elif expected_type == "string" and isinstance(value, str):
            return True, None
        elif expected_type == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True, None
        elif expected_type == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True, None
        elif expected_type == "boolean" and isinstance(value, bool):
            return True, None
        elif expected_type == "array" and isinstance(value, list):
            return True, None
        elif expected_type == "object" and isinstance(value, dict):
            return True, None
        else:
            return False, f"{field_name} must be of type {expected_type}"
    
    if not isinstance(value, expected_type):
        type_name = (
            expected_type.__name__ 
            if isinstance(expected_type, type) 
            else " or ".join(t.__name__ for t in expected_type)
        )
        return False, f"{field_name} must be of type {type_name}"
    
    return True, None


def validate_required(
    data: Dict[str, Any],
    required_fields: List[str]
) -> Tuple[bool, List[str]]:
    """
    Validate that all required fields are present in the data.
    
    Args:
        data: The data to validate.
        required_fields: List of required field names.
    
    Returns:
        A tuple containing a boolean indicating whether the data is valid,
        and a list of error messages if it's not.
    """
    errors = []
    
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"Required field '{field}' is missing")
    
    return len(errors) == 0, errors


def validate_string(
    value: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    field_name: str = "Value"
) -> Tuple[bool, Optional[str]]:
    """
    Validate a string against length and pattern constraints.
    
    Args:
        value: The string to validate.
        min_length: Minimum allowed length.
        max_length: Maximum allowed length.
        pattern: Regular expression pattern to match against.
        field_name: Name of the field being validated (for error messages).
    
    Returns:
        A tuple containing a boolean indicating whether the string is valid,
        and an optional error message if it's not.
    """
    if not isinstance(value, str):
        return False, f"{field_name} must be a string"
    
    if min_length is not None and len(value) < min_length:
        return False, f"{field_name} must be at least {min_length} characters long"
    
    if max_length is not None and len(value) > max_length:
        return False, f"{field_name} must be at most {max_length} characters long"
    
    if pattern is not None and not re.match(pattern, value):
        return False, f"{field_name} must match pattern {pattern}"
    
    return True, None


def validate_number(
    value: Union[int, float],
    minimum: Optional[Union[int, float]] = None,
    maximum: Optional[Union[int, float]] = None,
    field_name: str = "Value"
) -> Tuple[bool, Optional[str]]:
    """
    Validate a number against range constraints.
    
    Args:
        value: The number to validate.
        minimum: Minimum allowed value.
        maximum: Maximum allowed value.
        field_name: Name of the field being validated (for error messages).
    
    Returns:
        A tuple containing a boolean indicating whether the number is valid,
        and an optional error message if it's not.
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False, f"{field_name} must be a number"
    
    if minimum is not None and value < minimum:
        return False, f"{field_name} must be greater than or equal to {minimum}"
    
    if maximum is not None and value > maximum:
        return False, f"{field_name} must be less than or equal to {maximum}"
    
    return True, None


def validate_array(
    value: List[Any],
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    unique_items: bool = False,
    item_validator: Optional[Callable[[Any], Tuple[bool, Optional[str]]]] = None,
    field_name: str = "Value"
) -> Tuple[bool, Optional[str]]:
    """
    Validate an array against various constraints.
    
    Args:
        value: The array to validate.
        min_items: Minimum allowed number of items.
        max_items: Maximum allowed number of items.
        unique_items: Whether all items must be unique.
        item_validator: Optional function to validate each item.
        field_name: Name of the field being validated (for error messages).
    
    Returns:
        A tuple containing a boolean indicating whether the array is valid,
        and an optional error message if it's not.
    """
    if not isinstance(value, list):
        return False, f"{field_name} must be an array"
    
    if min_items is not None and len(value) < min_items:
        return False, f"{field_name} must contain at least {min_items} items"
    
    if max_items is not None and len(value) > max_items:
        return False, f"{field_name} must contain at most {max_items} items"
    
    if unique_items:
        # For simple items, use a set to check uniqueness
        if all(isinstance(item, (str, int, float, bool)) for item in value):
            if len(value) != len(set(value)):
                return False, f"{field_name} must contain unique items"
        # For complex items, use string representation for uniqueness check
        else:
            string_items = [str(item) for item in value]
            if len(string_items) != len(set(string_items)):
                return False, f"{field_name} must contain unique items"
    
    if item_validator:
        for i, item in enumerate(value):
            valid, error = item_validator(item)
            if not valid:
                return False, f"{field_name}[{i}]: {error}"
    
    return True, None


def deep_validate(
    data: Dict[str, Any],
    schema: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Perform deep validation of data against a schema.
    
    Args:
        data: The data to validate.
        schema: The schema to validate against. Should contain field definitions
               with types and constraints.
    
    Returns:
        A tuple containing a boolean indicating whether the data is valid,
        and a list of error messages if it's not.
    """
    errors = []
    
    # Check required fields
    required_fields = [
        field for field, field_schema in schema.items()
        if field_schema.get('required', False)
    ]
    valid, field_errors = validate_required(data, required_fields)
    if not valid:
        errors.extend(field_errors)
    
    # Validate fields
    for field_name, value in data.items():
        if field_name not in schema:
            if not schema.get('additional_properties', False):
                errors.append(f"Additional property '{field_name}' is not allowed")
            continue
        
        field_schema = schema[field_name]
        field_type = field_schema.get('type', 'any')
        
        # Validate type
        valid, error = validate_type(value, field_type, field_name)
        if not valid:
            errors.append(error)
            continue
        
        # Skip further validation if value is None
        if value is None:
            continue
        
        # Validate constraints based on type
        if field_type == 'string' and isinstance(value, str):
            valid, error = validate_string(
                value,
                min_length=field_schema.get('min_length'),
                max_length=field_schema.get('max_length'),
                pattern=field_schema.get('pattern'),
                field_name=field_name
            )
            if not valid:
                errors.append(error)
        
        elif field_type in ('integer', 'number') and isinstance(value, (int, float)):
            valid, error = validate_number(
                value,
                minimum=field_schema.get('minimum'),
                maximum=field_schema.get('maximum'),
                field_name=field_name
            )
            if not valid:
                errors.append(error)
        
        elif field_type == 'array' and isinstance(value, list):
            item_validator = None
            if 'items' in field_schema:
                items_schema = field_schema['items']
                item_validator = lambda item: validate_type(
                    item, items_schema.get('type', 'any')
                )
            
            valid, error = validate_array(
                value,
                min_items=field_schema.get('min_items'),
                max_items=field_schema.get('max_items'),
                unique_items=field_schema.get('unique_items', False),
                item_validator=item_validator,
                field_name=field_name
            )
            if not valid:
                errors.append(error)
        
        elif field_type == 'object' and isinstance(value, dict):
            if 'properties' in field_schema:
                valid, nested_errors = deep_validate(
                    value, field_schema['properties']
                )
                if not valid:
                    errors.extend(
                        f"{field_name}.{error}" for error in nested_errors
                    )
    
    return len(errors) == 0, errors
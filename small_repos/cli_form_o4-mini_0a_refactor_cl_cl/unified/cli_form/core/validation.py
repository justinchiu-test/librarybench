"""
Input validation functionality for CLI Form Library.
"""
import re
import typing as t
from datetime import datetime


def validate_input(
    value: t.Any, 
    field_name: t.Optional[str] = None,
    required: bool = False,
    min_value: t.Optional[t.Union[int, float]] = None,
    max_value: t.Optional[t.Union[int, float]] = None,
    regex: t.Optional[str] = None,
    max_length: t.Optional[int] = None
) -> t.Union[t.Dict[str, str], t.Tuple[bool, t.Optional[str]]]:
    """
    Validate input value based on provided constraints.
    
    Can be used in two ways:
    1. Single field validation: returns a tuple (valid, error_message)
    2. Multiple fields validation: input is a dict of field values, returns dict of field_name: error_message
    """
    # Case 1: Multiple fields validation
    if isinstance(value, dict):
        errors = {}
        for k, v in value.items():
            # Default validation rules for common fields
            if k == 'patient_id':
                if not v:
                    errors[k] = f"{k} is required"
                elif not re.match(r'^[A-Z0-9]{5,10}$', v):
                    errors[k] = f"{k} does not match pattern (5-10 uppercase letters or numbers)"
            elif k == 'phone':
                if not v:
                    errors[k] = f"{k} is required"
                elif not re.match(r'^\+\d{11,15}$', v):
                    errors[k] = f"{k} does not match pattern (+followed by 11-15 digits)"
            elif k == 'name':
                if not v:
                    errors[k] = f"{k} is required"
                elif len(v) > 50:
                    errors[k] = f"{k} exceeds max length (50)"
            # Add other specialized field validations here
        return errors
        
    # Case 2: Single field validation
    valid = True
    error_msg = None
    
    # Check if empty when required
    if required and not value:
        return False, f"This field is required"
        
    # Check numeric range
    if (min_value is not None or max_value is not None) and isinstance(value, (int, float)):
        if min_value is not None and value < min_value:
            valid = False
            error_msg = f"Value must be at least {min_value}"
        if max_value is not None and value > max_value:
            valid = False
            error_msg = f"Value must be at most {max_value}"
        if min_value is not None and max_value is not None and (value < min_value or value > max_value):
            valid = False
            error_msg = f"Value must be between {min_value} and {max_value}"
    
    # Check text patterns
    if isinstance(value, str):
        # Check length
        if max_length is not None and len(value) > max_length:
            valid = False
            error_msg = f"Text exceeds maximum length of {max_length}"
            
        # Check regex pattern
        if regex and not re.match(regex, value):
            valid = False
            error_msg = f"Text does not match required pattern"
            
        # Specialized field validations
        if field_name == "incident_id" and not re.match(r'^INC-\d{4}$', value):
            valid = False
            error_msg = "Incident ID must be in format INC-NNNN"
            
        elif field_name == "ip" and not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', value):
            valid = False
            error_msg = "Invalid IP address format"
            
        elif field_name == "general" and re.search(r'[<>]', value):
            valid = False
            error_msg = "Input contains invalid characters"
    
    return valid, error_msg if not valid else None
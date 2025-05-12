"""
Validation utilities for open-source maintainers.
"""
import os
import re

def validate_input(value, type_=None, range_=None, regex=None, exists=False):
    # Type check
    if type_ is not None:
        if not isinstance(value, type_):
            raise ValueError(f"Expected type {type_}, got {type(value)}")
    # Range check
    if range_ is not None:
        low, high = range_
        if not (low <= value <= high):
            raise ValueError(f"Value {value} out of range [{low}, {high}]")
    # Regex check
    if regex is not None:
        if not re.match(regex, str(value)):
            raise ValueError(f"Value {value} does not match regex {regex}")
    # Existence check
    if exists:
        if not os.path.exists(value):
            raise ValueError(f"Path does not exist: {value}")
    return True
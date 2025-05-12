"""
Various input validations for security analysts.
"""
import os
import re

def validate_input(value, regex=None, file_permissions=None, range_=None):
    # Regex validation
    if regex is not None:
        if not re.match(regex, value):
            raise ValueError(f"Value '{value}' does not match regex {regex}")
        return True
    # File permission validation
    if file_permissions is not None:
        try:
            mode = os.stat(value).st_mode & 0o777
        except Exception as e:
            raise ValueError(f"Cannot stat file: {value}")
        if mode != file_permissions:
            raise ValueError(f"File permissions {oct(mode)} do not match expected {oct(file_permissions)}")
        return True
    # Range validation (numeric)
    if range_ is not None:
        try:
            num = int(value)
        except Exception:
            raise ValueError(f"Value '{value}' is not an integer")
        low, high = range_
        if not (low <= num <= high):
            raise ValueError(f"Value {num} out of range [{low}, {high}]")
        return True
    # default pass-through
    return True
"""
Input validators for Open Source Maintainer CLI.
"""
import os
import re

def validate_input(value, type_=None, range_=None, regex=None, exists=False):
    if type_ is not None:
        if not isinstance(value, type_):
            raise ValueError(f"Type mismatch: {value}")
    if range_ is not None:
        val = int(value)
        minv, maxv = range_
        if val < minv or val > maxv:
            raise ValueError(f"Out of range: {value}")
    if regex is not None:
        if not re.match(regex, str(value)):
            raise ValueError(f"Regex mismatch: {value}")
    if exists:
        if not os.path.exists(value):
            raise ValueError(f"Path does not exist: {value}")
    return True
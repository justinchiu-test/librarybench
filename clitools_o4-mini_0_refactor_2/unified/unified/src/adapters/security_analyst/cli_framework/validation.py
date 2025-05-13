"""
Validation utilities for Security Analyst CLI.
"""
import os
import stat
import re

def validate_input(value, regex=None, file_permissions=None, range_=None):
    # Regex
    if regex is not None:
        if not re.match(regex, str(value)):
            raise ValueError(f"Regex mismatch: {value}")
    # File permissions
    if file_permissions is not None:
        if not os.path.exists(value):
            raise ValueError(f"File not found: {value}")
        st = os.stat(value)
        if stat.S_IMODE(st.st_mode) != file_permissions:
            raise ValueError(f"Permissions mismatch: {value}")
    # Range
    if range_ is not None:
        val = int(value)
        minv, maxv = range_
        if val < minv or val > maxv:
            raise ValueError(f"Out of range: {value}")
    return True
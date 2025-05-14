import os
import re

def validate_input(value, *, type_=None, range_=None, regex=None, exists=False):
    if type_ is not None and not isinstance(value, type_):
        raise ValueError(f"Value {value} is not of type {type_}")
    if range_ is not None:
        low, high = range_
        if not (low <= value <= high):
            raise ValueError(f"Value {value} not in range {range_}")
    if regex is not None:
        if not re.match(regex, str(value)):
            raise ValueError(f"Value {value} does not match {regex}")
    if exists:
        if not os.path.exists(value):
            raise ValueError(f"Path {value} does not exist")
    return True

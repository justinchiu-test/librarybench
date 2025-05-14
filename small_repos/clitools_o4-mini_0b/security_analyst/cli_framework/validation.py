import re
import os
import stat

def validate_input(value, regex=None, file_permissions=None, range_=None):
    if regex:
        if not re.match(regex, value):
            raise ValueError("Regex validation failed")
    if file_permissions and os.path.exists(value):
        st = os.stat(value).st_mode
        if stat.S_IMODE(st) != file_permissions:
            raise ValueError("File permissions invalid")
    if range_:
        minv, maxv = range_
        num = float(value)
        if num < minv or num > maxv:
            raise ValueError("Range validation failed")
    return True

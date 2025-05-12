"""
Utility functions for open-source maintainers.
"""
import datetime
import random
import string

def compute_default(key):
    # Build directory default
    if key == 'build_dir':
        return 'build'
    # Documentation directory with date
    if key == 'docs_dir':
        return 'docs_' + datetime.date.today().strftime('%Y%m%d')
    # Token generation
    if key == 'token':
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    # Unknown defaults
    return None
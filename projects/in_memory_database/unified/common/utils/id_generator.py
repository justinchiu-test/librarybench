"""
ID generation utilities.

This module provides functions for generating unique identifiers for various
purposes.
"""

import uuid
import time
import random
import string
from typing import Optional


def generate_uuid() -> str:
    """
    Generate a UUID-based identifier.
    
    Returns:
        A string containing a UUID.
    """
    return str(uuid.uuid4())


def generate_id(prefix: Optional[str] = None, length: int = 10) -> str:
    """
    Generate a unique ID with an optional prefix.
    
    Args:
        prefix: Optional prefix for the ID. If provided, the ID will be in the
               format "{prefix}-{random_part}".
        length: Length of the random part of the ID.
    
    Returns:
        A unique ID string.
    """
    timestamp = int(time.time() * 1000)
    random_part = ''.join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )
    
    if prefix:
        return f"{prefix}-{timestamp}-{random_part}"
    else:
        return f"{timestamp}-{random_part}"
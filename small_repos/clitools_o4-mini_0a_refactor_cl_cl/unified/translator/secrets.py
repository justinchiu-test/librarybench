"""
Secrets management for translator CLI tools.
"""

import os
from typing import Dict, Any, Optional


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a secret from environment variables.
    
    Args:
        key (str): Secret key (environment variable name).
        default (str, optional): Default value if key not found.
        
    Returns:
        str or None: Secret value or default.
    """
    return os.environ.get(key, default)
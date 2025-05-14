"""Adapter for backend_dev.microcli.env."""

from typing import Dict, Any, Optional

def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable.
    
    Args:
        key (str): Environment variable name
        default (str, optional): Default value if not found
    
    Returns:
        str or None: Environment variable value or default
    """
    import os
    return os.environ.get(key, default)

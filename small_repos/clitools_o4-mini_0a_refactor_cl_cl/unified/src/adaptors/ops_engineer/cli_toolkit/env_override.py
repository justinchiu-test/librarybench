"""Adapter for ops_engineer.cli_toolkit.env_override."""

from typing import Dict, Any, Optional

def get_env_overrides(prefix: str = '') -> Dict[str, str]:
    """Get environment variables as overrides.
    
    Args:
        prefix (str): Optional prefix for filtering variables
    
    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    import os
    
    if not prefix:
        return dict(os.environ)
    
    return {k: v for k, v in os.environ.items() if k.startswith(prefix)}

def apply_env_overrides(config: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
    """Apply environment overrides to configuration.
    
    Args:
        config (Dict[str, Any]): Configuration to override
        prefix (str): Optional prefix for filtering variables
    
    Returns:
        Dict[str, Any]: Updated configuration
    """
    overrides = get_env_overrides(prefix)
    result = config.copy()
    
    for key, value in overrides.items():
        if prefix and key.startswith(prefix):
            clean_key = key[len(prefix):]  # Remove prefix
            result[clean_key] = value
        elif not prefix:
            result[key] = value
            
    return result

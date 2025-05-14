"""Environment override for operations engineer CLI tools."""

import os
from typing import Dict, Any, Optional

def get_env_overrides(prefix: str = '') -> Dict[str, str]:
    """
    Get environment variables as overrides.

    Args:
        prefix (str): Environment variable prefix to filter by.

    Returns:
        Dict[str, str]: Dictionary of environment variables.
    """
    if not prefix:
        return dict(os.environ)

    return {k: v for k, v in os.environ.items() if k.startswith(prefix)}

def apply_env_overrides(config: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
    """
    Apply environment overrides to configuration.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
        prefix (str): Environment variable prefix to filter by.

    Returns:
        Dict[str, Any]: Configuration with environment overrides applied.
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

def env_override(config: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """
    Override configuration values with environment variables.

    Args:
        config (Dict[str, Any]): Configuration dictionary.
        prefix (str): Environment variable prefix.

    Returns:
        Dict[str, Any]: Configuration with environment overrides applied.
    """
    result = config.copy()

    # Check each key in the config for an environment override
    for key in config:
        env_key = f"{prefix.upper()}{key.upper()}"
        if env_key in os.environ:
            result[key] = os.environ[env_key]

    return result
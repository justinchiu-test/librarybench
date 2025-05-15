"""
Environment variable overrides for the CLI Toolkit.
"""
import os
import copy
from typing import Any, Dict, List, Optional, Set, Union

def apply_env_overrides(config: dict, prefix: str, separator: str = "__") -> dict:
    """
    Apply environment variable overrides to a configuration.
    
    Args:
        config: Configuration dictionary
        prefix: Environment variable prefix
        separator: Separator for nested keys
        
    Returns:
        New configuration with environment overrides applied
    """
    # Make a deep copy to avoid modifying the original
    result = copy.deepcopy(config)
    
    # Get all environment variables with the prefix
    env_vars = {k: v for k, v in os.environ.items() if k.startswith(prefix)}
    
    # Apply overrides
    for env_var, value in env_vars.items():
        # Remove prefix and convert to keys
        key_parts = env_var[len(prefix):].lstrip(separator).split(separator)
        
        # Convert value to appropriate type
        typed_value = _convert_value(value)
        
        # Apply override
        _set_nested_value(result, key_parts, typed_value)
    
    return result

def _convert_value(value: str) -> Any:
    """
    Convert a string value to an appropriate type.
    
    Args:
        value: String value
        
    Returns:
        Converted value
    """
    # Try to convert to boolean
    lower_value = value.lower()
    if lower_value in ("true", "yes", "1", "on"):
        return True
    if lower_value in ("false", "no", "0", "off"):
        return False
    
    # Try to convert to integer
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try to convert to float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Try to convert to list
    if value.startswith("[") and value.endswith("]"):
        items = value[1:-1].split(",")
        return [_convert_value(item.strip()) for item in items]
    
    # Keep as string
    return value

def _set_nested_value(config: dict, key_parts: List[str], value: Any) -> None:
    """
    Set a nested value in a configuration.
    
    Args:
        config: Configuration dictionary
        key_parts: List of keys to traverse
        value: Value to set
    """
    if not key_parts:
        return
    
    if len(key_parts) == 1:
        config[key_parts[0]] = value
        return
    
    # Create nested dictionaries as needed
    key = key_parts[0]
    if key not in config or not isinstance(config[key], dict):
        config[key] = {}
    
    _set_nested_value(config[key], key_parts[1:], value)

def get_env_vars_for_config(config: dict, prefix: str, separator: str = "__") -> Dict[str, str]:
    """
    Get environment variables for a configuration.
    
    Args:
        config: Configuration dictionary
        prefix: Environment variable prefix
        separator: Separator for nested keys
        
    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    
    def _collect_env_vars(config_part, key_parts=[]):
        for key, value in config_part.items():
            current_keys = key_parts + [key]
            
            if isinstance(value, dict):
                _collect_env_vars(value, current_keys)
            else:
                env_key = prefix + separator + separator.join(current_keys)
                env_vars[env_key] = str(value)
    
    _collect_env_vars(config)
    
    return env_vars

def export_to_env(config: dict, prefix: str, separator: str = "__") -> Dict[str, str]:
    """
    Export a configuration to environment variables.
    
    Args:
        config: Configuration dictionary
        prefix: Environment variable prefix
        separator: Separator for nested keys
        
    Returns:
        Dictionary of environment variables that were set
    """
    env_vars = get_env_vars_for_config(config, prefix, separator)
    
    # Set environment variables
    for key, value in env_vars.items():
        os.environ[key] = value
    
    return env_vars


def env_override(config: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """
    Override configuration values with environment variables.
    
    Args:
        config: Configuration dictionary to override
        prefix: Environment variable prefix
        
    Returns:
        Overridden configuration dictionary
    """
    # Create a copy of the original config
    result = config.copy()
    
    # Convert prefix to uppercase
    prefix = prefix.upper()
    
    # Look for environment variables with the given prefix
    for key in config.keys():
        env_key = f"{prefix}{key.upper()}"
        
        if env_key in os.environ:
            # Override value from environment
            result[key] = os.environ[env_key]
    
    return result
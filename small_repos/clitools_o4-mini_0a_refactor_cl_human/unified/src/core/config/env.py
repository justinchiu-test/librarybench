"""
Environment variable handling for CLI tools.
Enables overriding configuration with environment variables.
"""

import os
from typing import Any, Dict, Optional


class EnvOverride:
    """Handles environment variable overrides for configuration."""
    
    @staticmethod
    def apply_env_overrides(config: Dict[str, Any], 
                           prefix: str = "",
                           delimiter: str = "_",
                           lowercase_keys: bool = False) -> Dict[str, Any]:
        """
        Override configuration values with environment variables.
        
        Args:
            config: The configuration to override
            prefix: Prefix for environment variables (e.g., "APP_")
            delimiter: Delimiter for nested keys (e.g., "APP_DB_HOST")
            lowercase_keys: Whether to lowercase dictionary keys when matching
            
        Returns:
            Configuration with applied environment overrides
        """
        result = config.copy()
        
        # Process environment variables
        for env_key, env_value in os.environ.items():
            if not env_key.startswith(prefix):
                continue
            
            # Remove prefix
            key_path = env_key[len(prefix):]
            
            # Split path by delimiter
            parts = key_path.split(delimiter)
            
            # Apply the override
            EnvOverride._set_nested_value(result, parts, env_value, lowercase_keys)
            
        return result
    
    @staticmethod
    def _set_nested_value(config: Dict[str, Any], 
                         key_parts: list, 
                         value: str, 
                         lowercase_keys: bool) -> None:
        """
        Set a value in a nested dictionary based on key parts.
        
        Args:
            config: The configuration dictionary
            key_parts: List of nested key parts
            value: Value to set
            lowercase_keys: Whether to lowercase keys when matching
        """
        if not key_parts:
            return
        
        # Convert environment variable value to appropriate type
        typed_value = EnvOverride._convert_type(value)
        
        # Handle the simple case
        if len(key_parts) == 1:
            key = key_parts[0].lower() if lowercase_keys else key_parts[0]
            config[key] = typed_value
            return
        
        # Handle nested keys
        current = config
        for i, part in enumerate(key_parts):
            key = part.lower() if lowercase_keys else part
            
            if i == len(key_parts) - 1:
                # Last part, set the value
                current[key] = typed_value
            else:
                # Intermediate part, ensure the path exists
                if key not in current or not isinstance(current[key], dict):
                    current[key] = {}
                current = current[key]
    
    @staticmethod
    def _convert_type(value: str) -> Any:
        """
        Convert string value from environment to appropriate type.
        
        Args:
            value: String value from environment
            
        Returns:
            Converted value with appropriate type
        """
        # Boolean values
        if value.lower() in ('true', 'yes', 'y', '1'):
            return True
        if value.lower() in ('false', 'no', 'n', '0'):
            return False
        
        # Numeric values
        try:
            # Try as integer first
            return int(value)
        except ValueError:
            try:
                # Then as float
                return float(value)
            except ValueError:
                # Keep as string if not numeric
                return value


class EnvExporter:
    """Exports configuration to environment variables."""
    
    @staticmethod
    def export_to_env(config: Dict[str, Any], 
                     prefix: str = "",
                     delimiter: str = "_") -> Dict[str, str]:
        """
        Export configuration to environment variables.
        
        Args:
            config: The configuration to export
            prefix: Prefix for environment variables
            delimiter: Delimiter for nested keys
            
        Returns:
            Dictionary of environment variable names and values
        """
        env_vars = {}
        
        def _process_dict(d: Dict[str, Any], path: list) -> None:
            for key, value in d.items():
                new_path = path + [key]
                
                if isinstance(value, dict):
                    _process_dict(value, new_path)
                else:
                    env_key = prefix + delimiter.join(new_path)
                    # Convert value to string
                    env_vars[env_key] = EnvExporter._to_env_string(value)
        
        _process_dict(config, [])
        
        # Actually set the environment variables
        for key, value in env_vars.items():
            os.environ[key] = value
            
        return env_vars
    
    @staticmethod
    def _to_env_string(value: Any) -> str:
        """Convert a value to a string suitable for environment variables."""
        if value is None:
            return ""
        elif isinstance(value, bool):
            return "1" if value else "0"
        else:
            return str(value)
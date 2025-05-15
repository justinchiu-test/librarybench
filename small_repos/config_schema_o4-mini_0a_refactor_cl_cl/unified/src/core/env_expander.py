"""Environment variable expansion utility."""
import os
import re
from typing import Dict, Any, List, Union, Tuple


class EnvironmentExpander:
    """Utility class for expanding environment variables in configuration."""
    
    # Regular expressions for finding environment variables
    _env_var_pattern = re.compile(r'\$([a-zA-Z_][a-zA-Z0-9_]*|\{([a-zA-Z_][a-zA-Z0-9_]*)\})')
    
    @classmethod
    def expand(cls, value: Any) -> Any:
        """Recursively expand environment variables in a value.
        
        Args:
            value: The value to expand environment variables in
            
        Returns:
            The value with environment variables expanded
        """
        if isinstance(value, str):
            return cls._expand_str(value)
        elif isinstance(value, list):
            return [cls.expand(item) for item in value]
        elif isinstance(value, dict):
            return {k: cls.expand(v) for k, v in value.items()}
        else:
            return value
            
    @classmethod
    def _expand_str(cls, value: str) -> str:
        """Expand environment variables in a string.
        
        Args:
            value: The string to expand environment variables in
            
        Returns:
            The string with environment variables expanded
        """
        def _replace_var(match):
            var_name = match.group(1)
            if var_name.startswith('{') and var_name.endswith('}'):
                var_name = var_name[1:-1]
            return os.environ.get(var_name, match.group(0))
            
        return re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*|\{[a-zA-Z_][a-zA-Z0-9_]*\})', _replace_var, value)


def expand_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Expand environment variables in a configuration dictionary.
    
    Args:
        config: The configuration dictionary
        
    Returns:
        A new dictionary with environment variables expanded
    """
    return EnvironmentExpander.expand(config)
import os
import copy

def env_override(config: dict, prefix: str) -> dict:
    """
    Override configuration values with environment variables.
    
    Args:
        config: The configuration dictionary
        prefix: The prefix to use for environment variables
        
    Returns:
        A new configuration with values overridden from environment variables
    """
    result = copy.deepcopy(config)
    
    for key in config:
        env_var = f"{prefix}_{key}".upper()
        if env_var in os.environ:
            value = os.environ[env_var]
            
            # Type conversion based on original value type
            if isinstance(config[key], bool):
                result[key] = value.lower() in ("true", "yes", "1", "on")
            elif isinstance(config[key], int):
                result[key] = int(value)
            elif isinstance(config[key], float):
                result[key] = float(value)
            else:
                result[key] = value
                
    return result
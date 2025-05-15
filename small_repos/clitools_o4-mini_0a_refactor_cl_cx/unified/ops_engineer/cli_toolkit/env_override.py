import os

def env_override(config, prefix):
    """
    Override configuration values with environment variables
    
    Args:
        config: Configuration dictionary
        prefix: Environment variable prefix
        
    Returns:
        dict: Updated configuration with environment overrides
    """
    result = config.copy()
    
    for key in config:
        # Construct environment variable name with prefix
        env_key = f"{prefix}{key}".upper()
        
        # Check if environment variable exists
        if env_key in os.environ:
            # Update the configuration with the environment value
            result[key] = os.environ[env_key]
                
    return result
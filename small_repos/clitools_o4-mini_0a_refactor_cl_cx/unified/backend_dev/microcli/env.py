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
    
    for key, value in config.items():
        # Construct environment variable name with prefix
        env_key = f"{prefix}_{key}".upper()
        
        # Check if environment variable exists
        if env_key in os.environ:
            env_value = os.environ[env_key]
            
            # Type conversion based on original value type
            if isinstance(value, bool):
                # Convert string to boolean
                result[key] = env_value.lower() in ('true', 'yes', '1')
            elif isinstance(value, int):
                # Convert string to integer
                result[key] = int(env_value)
            elif isinstance(value, float):
                # Convert string to float
                result[key] = float(env_value)
            elif isinstance(value, list):
                # Assume comma-separated list
                result[key] = env_value.split(',')
            else:
                # Default to string
                result[key] = env_value
                
    return result
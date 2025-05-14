"""Environment utilities for backend developer CLI tools."""

import os
import json

def get_env(key, default=None):
    """Get environment variable."""
    return os.environ.get(key, default)

def env_override(config, prefix):
    """
    Override config values with environment variables.

    Args:
        config: Configuration dictionary
        prefix: Environment variable prefix

    Returns:
        Updated configuration
    """
    result = config.copy()

    for env_key, env_value in os.environ.items():
        if env_key.startswith(prefix.upper() + "_"):
            # Extract config key (lowercased)
            config_key = env_key[len(prefix) + 1:].lower()

            if config_key in result:
                # Convert to appropriate type based on the original value
                if isinstance(result[config_key], bool):
                    # Convert to boolean
                    result[config_key] = env_value.lower() in ("true", "yes", "1", "on")
                elif isinstance(result[config_key], int):
                    # Convert to integer
                    try:
                        result[config_key] = int(env_value)
                    except ValueError:
                        pass  # Ignore invalid values
                elif isinstance(result[config_key], float):
                    # Convert to float
                    try:
                        result[config_key] = float(env_value)
                    except ValueError:
                        pass  # Ignore invalid values
                elif isinstance(result[config_key], dict):
                    # Try to parse as JSON
                    try:
                        result[config_key] = json.loads(env_value)
                    except json.JSONDecodeError:
                        pass  # Ignore invalid values
                elif isinstance(result[config_key], list):
                    # Split by comma
                    result[config_key] = [item.strip() for item in env_value.split(",")]
                else:
                    # Use as string
                    result[config_key] = env_value

    return result
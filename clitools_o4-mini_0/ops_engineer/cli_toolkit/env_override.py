import os

def env_override(config, prefix):
    """
    Override config values with environment variables using prefix.
    """
    result = dict(config)
    for key in config:
        env_key = f"{prefix}{key}".upper()
        if env_key in os.environ:
            result[key] = os.environ[env_key]
    return result

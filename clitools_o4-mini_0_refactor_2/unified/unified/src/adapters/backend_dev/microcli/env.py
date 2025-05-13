"""
Environment variable overrides for backend_dev microcli.
"""
import os

def env_override(config, prefix):
    """
    Override config values from environment variables.
    prefix: prefix for environment variables, case-insensitive.
    """
    new = config.copy()
    for key, val in config.items():
        envvar = f"{prefix.upper()}_{key.upper()}"
        env_val = os.getenv(envvar)
        if env_val is not None:
            if isinstance(val, bool):
                new[key] = env_val.lower() in ("1", "true", "yes")
            elif isinstance(val, int):
                new[key] = int(env_val)
            else:
                new[key] = env_val
    return new
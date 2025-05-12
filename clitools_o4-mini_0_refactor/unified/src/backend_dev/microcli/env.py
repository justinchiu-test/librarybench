"""
Environment variable overrides for backend developers.
"""
import os

def env_override(config, prefix):
    new = {}
    for key, val in config.items():
        env_key = f"{prefix.upper()}_{key.upper()}"
        if env_key in os.environ:
            raw = os.environ[env_key]
            if isinstance(val, bool):
                new[key] = raw.lower() in ('1', 'true', 'yes', 'on')
            elif isinstance(val, int):
                try:
                    new[key] = int(raw)
                except ValueError:
                    new[key] = val
            elif isinstance(val, float):
                try:
                    new[key] = float(raw)
                except ValueError:
                    new[key] = val
            else:
                new[key] = raw
        else:
            new[key] = val
    return new
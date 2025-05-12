"""
Environment variable overrides for ops engineers.
"""
import os

def env_override(config, prefix):
    new_conf = {}
    pref = prefix.upper()
    for key, val in config.items():
        env_key = f"{pref}{key.upper()}"
        if env_key in os.environ:
            new_conf[key] = os.environ[env_key]
        else:
            new_conf[key] = val
    return new_conf
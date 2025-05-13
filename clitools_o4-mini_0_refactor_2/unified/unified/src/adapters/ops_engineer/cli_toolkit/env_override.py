"""
Override configuration values from environment variables for Operations Engineer CLI.
"""
import os

def env_override(config, prefix):
    new = {}
    pu = prefix.upper()
    for k, v in config.items():
        envvar = f"{pu}{k.upper()}"
        new[k] = os.getenv(envvar, v)
    return new
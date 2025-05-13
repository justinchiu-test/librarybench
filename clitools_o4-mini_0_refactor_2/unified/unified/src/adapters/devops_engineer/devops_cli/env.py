"""
Environment overrides for DevOps Engineer CLI.
"""
import os

def env_override(config, prefix='DEVOPS'):
    new = {}
    for section, entries in config.items():
        new_section = {}
        for k, v in entries.items():
            envvar = f"{prefix}_{k.upper()}"
            if envvar in os.environ:
                new_section[k] = os.environ[envvar]
            else:
                new_section[k] = v
        new[section] = new_section
    return new
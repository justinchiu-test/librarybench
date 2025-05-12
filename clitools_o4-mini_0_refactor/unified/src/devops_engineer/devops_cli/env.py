"""
Environment variable overrides for devops engineers.
"""
import os

def env_override(config):
    # Prefix for devops engineer env vars
    prefix = 'DEVOPS'
    new_conf = {}
    for section, entries in config.items():
        new_entries = {}
        for key, val in entries.items():
            env_key = f"{prefix}_{key.upper()}"
            if env_key in os.environ:
                raw = os.environ[env_key]
                if isinstance(val, bool):
                    new_entries[key] = raw.lower() in ('1', 'true', 'yes', 'on')
                elif isinstance(val, int):
                    new_entries[key] = int(raw)
                elif isinstance(val, float):
                    new_entries[key] = float(raw)
                else:
                    new_entries[key] = raw
            else:
                new_entries[key] = val
        new_conf[section] = new_entries
    return new_conf
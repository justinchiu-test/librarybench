"""
Environment overrides for security analysts.
"""
def env_override(env_vars, keys):
    # env_vars: dict of environment variables; keys: list of keys to extract
    result = {}
    for key in keys:
        env_key = f"SEC_{key}"
        if env_key in env_vars:
            result[key] = env_vars[env_key]
    return result
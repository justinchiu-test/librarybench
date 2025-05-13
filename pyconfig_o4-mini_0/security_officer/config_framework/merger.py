def merge_configs(defaults, vault, env):
    result = defaults.copy()
    result.update(vault or {})
    result.update(env or {})
    return result

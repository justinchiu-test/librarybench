def env_override(env_vars, whitelist):
    result = {}
    for k, v in env_vars.items():
        if not k.startswith("SEC_"):
            continue
        key = k[len("SEC_"):]
        if key in whitelist:
            result[key] = v
    return result

import os

def env_override(config, prefix="DEVOPS_"):
    new_conf = {}
    for section, values in config.items():
        nv = {}
        for k, v in values.items():
            env_key = f"{prefix}{k}".upper()
            if env_key in os.environ:
                nv[k] = os.environ[env_key]
            else:
                nv[k] = v
        new_conf[section] = nv
    return new_conf

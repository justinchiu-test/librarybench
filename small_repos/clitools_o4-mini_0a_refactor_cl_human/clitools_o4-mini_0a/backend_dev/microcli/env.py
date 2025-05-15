import os

def env_override(config: dict, prefix: str) -> dict:
    result = config.copy()
    for key, value in config.items():
        env_key = f"{prefix}_{key}".upper()
        if env_key in os.environ:
            new = os.environ[env_key]
            # try to cast
            if isinstance(value, bool):
                result[key] = new.lower() in ("1", "true", "yes")
            elif isinstance(value, int):
                result[key] = int(new)
            elif isinstance(value, float):
                result[key] = float(new)
            else:
                result[key] = new
    return result

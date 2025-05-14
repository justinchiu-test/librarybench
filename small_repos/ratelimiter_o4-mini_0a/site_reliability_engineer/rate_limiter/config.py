def validate_config(cfg):
    if not isinstance(cfg, dict):
        raise ValueError("Config must be a dict")
    required = ["name", "rate", "capacity"]
    for field in required:
        if field not in cfg:
            raise ValueError(f"Missing field: {field}")
    if not isinstance(cfg["name"], str):
        raise ValueError("Field 'name' must be a string")
    if not isinstance(cfg["rate"], (int, float)) or cfg["rate"] < 0:
        raise ValueError("Field 'rate' must be a non-negative number")
    if not isinstance(cfg["capacity"], int) or cfg["capacity"] < 1:
        raise ValueError("Field 'capacity' must be an integer >= 1")
    return True

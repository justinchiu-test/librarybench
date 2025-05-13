# interactive_cli
def prompt_missing(config: dict, required_keys: list) -> dict:
    """
    Prompt the user for missing keys in config.
    Returns a new config with prompted values filled in.
    """
    new_cfg = config.copy()
    for key in required_keys:
        if key not in new_cfg or new_cfg[key] is None:
            value = input(f"Enter value for '{key}': ")
            new_cfg[key] = value
    return new_cfg

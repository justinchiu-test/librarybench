import yaml
from pathlib import Path
import toml  # will pick up our top-level toml.py

def load_config(path):
    data = Path(path).read_text()
    if path.endswith((".yaml", ".yml")):
        cfg = yaml.safe_load(data)
    elif path.endswith(".toml"):
        cfg = toml.loads(data)
    else:
        raise ValueError("Unsupported config format")
    if not isinstance(cfg, dict):
        raise ValueError("Invalid config structure")
    for key in ("include", "exclude"):
        if key not in cfg or not isinstance(cfg[key], list):
            raise ValueError(f"Config missing list '{key}'")
    return cfg

import os
import json
import configparser

# For TOML parsing: use stdlib tomllib if available; otherwise, fallback to external toml if installed.
try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None

# YAML support is optional; tests will pick up our yaml.py stub if no real PyYAML is installed.
try:
    import yaml
except ModuleNotFoundError:
    yaml = None

def load_config(file_path, profile=None):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file {file_path} not found")

    ext = os.path.splitext(file_path)[1].lower()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {}
    if ext == '.json':
        data = json.loads(content)

    elif ext in ('.yaml', '.yml'):
        if yaml is None:
            raise ValueError("YAML support is not available")
        data = yaml.safe_load(content)

    elif ext == '.toml':
        # Prefer stdlib tomllib
        if tomllib is not None:
            data = tomllib.loads(content)
        else:
            # Fallback to external toml package if available
            try:
                import toml as _toml
            except ImportError:
                raise ValueError("TOML support is not available")
            data = _toml.loads(content)

    elif ext in ('.ini', '.cfg'):
        parser = configparser.ConfigParser()
        parser.read_string(content)
        if profile:
            if profile in parser:
                data = dict(parser[profile])
            else:
                raise KeyError(f"Profile {profile} not found in config")
        else:
            data = {}
            for section in parser.sections():
                data[section] = dict(parser[section])

    else:
        raise ValueError(f"Unsupported config format: {ext}")

    # If a profile is requested for non-INI formats, return that sub-dictionary
    if profile and ext not in ('.ini', '.cfg') and isinstance(data, dict):
        return data.get(profile, {})

    return data

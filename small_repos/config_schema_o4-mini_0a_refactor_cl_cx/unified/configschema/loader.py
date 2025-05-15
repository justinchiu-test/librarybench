"""
Configuration file loaders for JSON, YAML, and INI formats, with caching.
"""
import os
import json
import configparser

# Try to import YAML support
try:
    import yaml
except ImportError:
    yaml = None

from .cache import _cache
from .env import expand_env_vars
from .config import ConfigManager

def _convert_ini_value(v):
    """Convert INI string to int, float, bool, list or leave as string."""
    lv = v.strip()
    lower = lv.lower()
    if lower in ('true', 'false'):
        return lower == 'true'
    if ',' in lv:
        return [item for item in lv.split(',')]
    try:
        return int(lv)
    except Exception:
        pass
    try:
        return float(lv)
    except Exception:
        pass
    return lv

def load_json(path):
    """Load JSON file and return as dict."""
    with open(path, 'r') as f:
        return json.load(f)

def load_ini(path):
    """Load INI file and return as dict."""
    cp = configparser.ConfigParser()
    cp.read(path)
    # If only DEFAULT section, return defaults
    if not cp.sections():
        return {k: _convert_ini_value(v) for k, v in cp.defaults().items()}
    result = {}
    for section in cp.sections():
        sect = {}
        for k, v in cp[section].items():
            # preserve raw string values for named sections
            sect[k] = v
        result[section] = sect
    return result

def load_yaml(path):
    """Load YAML file and return as Python object."""
    if yaml is None:
        raise ImportError("PyYAML is not installed")
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def load_config(path):
    """Load configuration file with caching and return a ConfigManager."""
    path = str(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    mtime = os.path.getmtime(path)
    # Return cached if unmodified
    if path in _cache and _cache[path][0] == mtime:
        return _cache[path][1]
    # Select loader by extension
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        data = load_json(path)
    elif ext in ('.ini',):
        data = load_ini(path)
    elif ext in ('.yaml', '.yml'):
        if yaml is None:
            raise RuntimeError("YAML support not available")
        data = load_yaml(path)
    else:
        raise RuntimeError(f"Unsupported config file format: {path}")
    # Expand environment variables
    data = expand_env_vars(data)
    # Wrap in ConfigManager
    mgr = ConfigManager(data, path)
    # Cache
    _cache[path] = (mtime, mgr)
    return mgr
import os
import sys
import logging
import copy

# Plugin registry
plugin_registry = {}

def register_plugin(name, loader):
    if name in plugin_registry:
        raise KeyError(f"Plugin '{name}' already registered")
    if not callable(loader):
        raise ValueError("Loader must be callable")
    plugin_registry[name] = loader

def log_event(event_type, message):
    logger = logging.getLogger('config_manager')
    logger.info(f"{event_type}:{message}")

def validate_config(config, schema):
    missing = []
    for key in schema.get('required', []):
        if key not in config:
            missing.append(key)
    if missing:
        log_event('validation_error', f"Missing required keys: {missing}")
        raise ValueError(f"Missing required keys: {missing}")
    for key, prop in schema.get('properties', {}).items():
        if key in config and 'type' in prop:
            expected = prop['type']
            type_map = {
                'string': str,
                'number': (int, float),
                'integer': int,
                'boolean': bool,
                'object': dict,
                'array': list
            }
            if expected in type_map and not isinstance(config[key], type_map[expected]):
                log_event('validation_error', f"Type mismatch for {key}: expected {expected}")
                raise TypeError(f"Type mismatch for {key}: expected {expected}")
    log_event('validation_success', "Config validated successfully")
    return True

def export_to_env(config, inject=True):
    def _flatten(d, parent_key=''):
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(_flatten(v, new_key))
            else:
                items[new_key.upper()] = v
        return items
    flat = _flatten(config)
    lines = []
    for k, v in flat.items():
        line = f"{k}={v}"
        lines.append(line)
        if inject:
            os.environ[k] = str(v)
    return lines

def get_namespace(config, path):
    parts = path.split('.')
    current = config
    for p in parts:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            raise KeyError(f"Namespace '{path}' not found")
    return current

def snapshot(config):
    return copy.deepcopy(config)

def load_toml_source(path):
    """
    Load a TOML configuration from the given file path.
    Tries to use the 'toml' library; if unavailable, falls back to the
    standard library 'tomllib' (Python 3.11+).
    """
    try:
        import toml
        # toml.load can accept a file path or file object, depending on implementation
        # If it expects a file object, let it open internally; else we provide the path
        return toml.load(path)
    except ImportError:
        import tomllib
        with open(path, 'rb') as f:
            return tomllib.load(f)

def diff_changes(old, new):
    def _flatten(d, parent_key=''):
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(_flatten(v, new_key))
            else:
                items[new_key] = v
        return items
    old_flat = _flatten(old)
    new_flat = _flatten(new)
    diffs = {}
    keys = set(old_flat.keys()).union(new_flat.keys())
    for k in keys:
        o = old_flat.get(k)
        n = new_flat.get(k)
        if o != n:
            diffs[k] = (o, n)
    return diffs

def override_config(config, overrides):
    for k, v in overrides.items():
        if isinstance(v, dict) and isinstance(config.get(k), dict):
            override_config(config[k], v)
        else:
            config[k] = v
    return config

def parse_cli_args(args=None):
    if args is None:
        args = sys.argv[1:]
    overrides = {}
    idx = 0
    while idx < len(args):
        arg = args[idx]
        if arg.startswith('--'):
            if '=' in arg:
                key, val = arg[2:].split('=', 1)
            else:
                key = arg[2:]
                idx += 1
                if idx < len(args):
                    val = args[idx]
                else:
                    break
            # cast to bool/int/float if possible
            if isinstance(val, str) and val.lower() in ('true', 'false'):
                val_cast = val.lower() == 'true'
            else:
                try:
                    if isinstance(val, str) and '.' in val:
                        val_cast = float(val)
                    else:
                        val_cast = int(val)
                except Exception:
                    val_cast = val
            overrides[key.replace('-', '_')] = val_cast
        idx += 1
    return overrides

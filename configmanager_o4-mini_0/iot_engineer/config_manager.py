import os
import json
import logging
import argparse
import copy

# Try to import toml library
try:
    import tomllib as toml
except ImportError:
    try:
        import toml
    except ImportError:
        toml = None

# Logger setup
logger = logging.getLogger('config_manager')
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Module-level state
plugins = {}
snapshots = {}
_snapshot_counter = 0

class ConfigValidationError(Exception):
    def __init__(self, errors):
        super().__init__('Configuration validation failed')
        self.errors = errors

def register_plugin(name, loader_fn):
    if not callable(loader_fn):
        raise ValueError("loader_fn must be callable")
    plugins[name] = loader_fn

def validate_config(cfg, schema):
    errors = []
    def _validate(node, sch, path=''):
        if not isinstance(sch, dict):
            return
        for key, rule in sch.items():
            p = f"{path}.{key}" if path else key
            if key not in node:
                errors.append(f"Missing key: {p}")
            else:
                val = node[key]
                if isinstance(rule, dict):
                    if not isinstance(val, dict):
                        errors.append(f"Expected dict at {p}")
                    else:
                        _validate(val, rule, p)
                else:
                    typ = rule
                    mapping = {
                        'int': int, 'float': float,
                        'str': str, 'bool': bool,
                        'dict': dict, 'list': list
                    }
                    expected = mapping.get(typ)
                    if expected and not isinstance(val, expected):
                        errors.append(f"Expected {typ} at {p}, got {type(val).__name__}")
    _validate(cfg, schema)
    if errors:
        raise ConfigValidationError(errors)
    return True

def export_to_env(cfg, to_shell=True, set_env=True):
    lines = []
    def _flatten(d, parent=''):
        for k, v in d.items():
            name = f"{parent}_{k}" if parent else k
            if isinstance(v, dict):
                yield from _flatten(v, name)
            else:
                yield name.upper(), str(v)
    for key, val in _flatten(cfg):
        if set_env:
            os.environ[key] = val
        if to_shell:
            lines.append(f"export {key}='{val}'")
    return lines

def log_event(event_type, message, data=None):
    record = {'event': event_type, 'message': message}
    if data is not None:
        record['data'] = data
    logger.info(json.dumps(record))

def get_namespace(cfg, namespace):
    parts = namespace.split('.')
    node = cfg
    for p in parts:
        if not isinstance(node, dict) or p not in node:
            return {}
        node = node[p]
    return node

def snapshot(cfg):
    global _snapshot_counter
    snap = copy.deepcopy(cfg)
    sid = _snapshot_counter
    snapshots[sid] = snap
    _snapshot_counter += 1
    return sid

def get_snapshot(sid):
    return copy.deepcopy(snapshots.get(sid))

def load_toml_source(path, base_cfg):
    if toml is None:
        raise RuntimeError("TOML support not available")
    with open(path, 'rb') as f:
        data = toml.load(f)
    return override_config(base_cfg, data)

def diff_changes(old, new):
    added = {}
    removed = {}
    changed = {}
    def _recurse(o, n, path=''):
        o_keys = set(o.keys()) if isinstance(o, dict) else set()
        n_keys = set(n.keys()) if isinstance(n, dict) else set()
        for key in n_keys - o_keys:
            added[f"{path}{key}"] = n[key]
        for key in o_keys - n_keys:
            removed[f"{path}{key}"] = o[key]
        for key in o_keys & n_keys:
            ov = o[key]
            nv = n[key]
            p = f"{path}{key}"
            if isinstance(ov, dict) and isinstance(nv, dict):
                _recurse(ov, nv, p + '.')
            elif ov != nv:
                changed[p] = {'old': ov, 'new': nv}
    _recurse(old or {}, new or {})
    return {'added': added, 'removed': removed, 'changed': changed}

def override_config(cfg, overrides):
    result = copy.deepcopy(cfg)
    def _merge(a, b):
        for key, val in b.items():
            if key in a and isinstance(a[key], dict) and isinstance(val, dict):
                _merge(a[key], val)
            else:
                a[key] = val
    _merge(result, overrides)
    return result

def parse_cli_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--simulate-gps', action='store_true')
    parsed = parser.parse_args(args=args)
    return vars(parsed)

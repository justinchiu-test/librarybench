# coding: utf-8
"""
iot_engineer configuration utilities
"""
import os
import json
import logging

# Plugin registry
plugins = {}

class ConfigValidationError(Exception):
    """Raised when configuration validation errors occur"""
    def __init__(self, errors):
        super().__init__('; '.join(errors))
        self.errors = errors

def register_plugin(name, loader):
    if not callable(loader):
        raise ValueError('loader must be callable')
    plugins[name] = loader

def validate_config(cfg, schema):
    errors = []
    def _check(d, s, prefix=''):
        for key, rule in s.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(rule, dict):
                # nested schema
                if key in d and isinstance(d[key], dict):
                    _check(d[key], rule, path)
                else:
                    errors.append(f"Missing key: {path}")
            else:
                # rule is type string
                val = d.get(key)
                if val is None:
                    errors.append(f"Missing key: {path}")
                else:
                    expected = int if rule == 'int' else str if rule == 'str' else None
                    if expected and not isinstance(val, expected):
                        errors.append(f"Expected {rule} at {path}")
    _check(cfg or {}, schema or {})
    if errors:
        raise ConfigValidationError(errors)
    return True

def export_to_env(cfg):
    # flatten nested dict into uppercase keys separated by underscore
    def _flatten_env(d, prefix=''):
        for k, v in d.items():
            name = f"{prefix}_{k}" if prefix else k
            if isinstance(v, dict):
                yield from _flatten_env(v, name)
            else:
                yield name.upper(), v
    lines = []
    for k, v in _flatten_env(cfg):
        os.environ[k] = str(v)
        lines.append(f"export {k}='{v}'")
    return lines

def _flatten(d, prefix=''):
    items = {}
    for k, v in d.items():
        name = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            items.update(_flatten(v, name))
        else:
            items[name] = v
    return items

def log_event(event, message, data=None):
    import json
    payload = {'event': event, 'message': message}
    if data is not None:
        payload['data'] = data
    logging.info(json.dumps(payload))

def get_namespace(cfg, path):
    node = cfg
    for p in path.split('.'):
        if isinstance(node, dict) and p in node:
            node = node[p]
        else:
            return {}
    return node

# Snapshot storage
_snapshots = {}
_next_snapshot_id = 1

def snapshot(cfg):
    import copy
    global _next_snapshot_id
    sid = _next_snapshot_id
    _snapshots[sid] = copy.deepcopy(cfg)
    _next_snapshot_id += 1
    return sid

def get_snapshot(sid):
    import copy
    if sid not in _snapshots:
        return None
    return copy.deepcopy(_snapshots[sid])

def load_toml_source(path, base=None):
    try:
        import tomllib as _tl
        with open(path, 'rb') as f:
            data = _tl.load(f)
    except ImportError:
        try:
            import toml as _tl
            data = _tl.loads(open(path, 'r').read())
        except Exception:
            data = {}
    # merge into base
    import copy
    result = copy.deepcopy(base) if base else {}
    _deep_merge(result, data)
    return result

def _deep_merge(a, b):
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            _deep_merge(a[k], v)
        else:
            a[k] = v
    return a

def diff_changes(old, new):
    old_flat = _flatten(old or {})
    new_flat = _flatten(new or {})
    added = {k: new_flat[k] for k in new_flat if k not in old_flat}
    removed = {k: old_flat[k] for k in old_flat if k not in new_flat}
    changed = {k: {'old': old_flat[k], 'new': new_flat[k]} for k in old_flat if k in new_flat and old_flat[k] != new_flat[k]}
    return {'added': added, 'removed': removed, 'changed': changed}

def override_config(cfg, overrides):
    import copy
    base = copy.deepcopy(cfg or {})
    return _deep_merge(base, overrides or {})

def parse_cli_args(args):
    overrides = {}
    for arg in args:
        if arg.startswith('--'):
            key = arg[2:]
            if '=' in key:
                k, val = key.split('=', 1)
            else:
                k = key
                val = 'true'
            k = k.replace('-', '_')
            v_lower = val.lower()
            if v_lower == 'true':
                parsed = True
            elif v_lower == 'false':
                parsed = False
            else:
                try:
                    parsed = int(val)
                except ValueError:
                    try:
                        parsed = float(val)
                    except ValueError:
                        parsed = val
            overrides[k] = parsed
    return overrides
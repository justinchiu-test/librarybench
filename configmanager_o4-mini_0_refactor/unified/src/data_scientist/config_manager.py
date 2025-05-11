# coding: utf-8
"""
data_scientist configuration utilities
"""
import os
import sys
import json
import logging

# Plugin registry
plugin_registry = {}

def register_plugin(name, loader):
    if name in plugin_registry:
        raise KeyError(f"Plugin '{name}' already registered")
    if not callable(loader):
        raise ValueError("loader must be callable")
    plugin_registry[name] = loader

def validate_config(config, schema):
    # Check required fields
    required = schema.get('required', [])
    for key in required:
        if key not in config:
            raise ValueError(f"Missing required key: {key}")
    # Check property types
    props = schema.get('properties', {})
    for key, rule in props.items():
        if key in config:
            expected = rule.get('type')
            val = config[key]
            if expected == 'integer':
                if not isinstance(val, int):
                    raise TypeError(f"Expected integer for key {key}")
            if expected == 'string':
                if not isinstance(val, str):
                    raise TypeError(f"Expected string for key {key}")
    logging.info('validation_success')
    return True

def export_to_env(cfg, inject=True):
    lines = []
    def flatten(d, prefix=''):
        for k, v in d.items():
            name = f"{prefix}_{k}" if prefix else k
            if isinstance(v, dict):
                yield from flatten(v, name)
            else:
                yield name.upper(), str(v)
    for k, v in flatten(cfg):
        line = f"{k}={v}"
        lines.append(line)
        if inject:
            os.environ[k] = v
    return lines

def get_namespace(cfg, path):
    parts = path.split('.')
    node = cfg
    for p in parts:
        if isinstance(node, dict) and p in node:
            node = node[p]
        else:
            raise KeyError(f"Namespace '{path}' not found")
    return node

def snapshot(cfg):
    return json.loads(json.dumps(cfg))

def load_toml_source(path):
    try:
        import tomllib as tl
        with open(path, 'rb') as f:
            return tl.load(f)
    except ImportError:
        try:
            import toml as tl
            return tl.loads(open(path, 'r').read())
        except ImportError:
            raise

def diff_changes(old, new):
    def flatten(d, prefix=''):
        items = {}
        for k, v in d.items():
            name = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                items.update(flatten(v, name))
            else:
                items[name] = v
        return items
    old_flat = flatten(old or {})
    new_flat = flatten(new or {})
    diffs = {}
    keys = set(old_flat) | set(new_flat)
    for k in keys:
        o = old_flat.get(k)
        n = new_flat.get(k)
        if o != n:
            diffs[k] = (o, n)
    return diffs

def override_config(cfg, overrides):
    # deep merge without modifying originals
    import copy
    result = copy.deepcopy(cfg or {})
    def merge(a, b):
        for k, v in b.items():
            if k in a and isinstance(a[k], dict) and isinstance(v, dict):
                merge(a[k], v)
            else:
                a[k] = v
        return a
    return merge(result, overrides or {})

def parse_cli_args():
    import sys
    args = sys.argv[1:]
    overrides = {}
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('--'):
            if '=' in arg:
                key, val = arg[2:].split('=', 1)
            else:
                key = arg[2:]
                if i + 1 < len(args) and not args[i + 1].startswith('-'):
                    val = args[i + 1]
                    i += 1
                else:
                    val = 'true'
            key = key.replace('-', '_')
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
            overrides[key] = parsed
        i += 1
    return overrides

def log_event(event, message):
    logging.info(f"{event}:{message}")
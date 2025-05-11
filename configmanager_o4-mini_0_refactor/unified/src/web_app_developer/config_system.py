# coding: utf-8
"""
Web app developer configuration system
"""
import logging
import json

class ConfigSystem:
    def __init__(self):
        self.config = {}
        # plugin_name -> (loader, callback)
        self.plugins = {}

    def register_plugin(self, name, loader, callback):
        self.plugins[name] = (loader, callback)

    def load_plugin(self, name):
        if name not in self.plugins:
            raise KeyError(f"Plugin '{name}' not registered")
        loader, callback = self.plugins[name]
        result = loader()
        # replace config
        self.config = result or {}
        # invoke callback
        try:
            callback(self.config)
        except Exception:
            pass
        # log load event
        logging.info('plugin_loaded')
        return result

    def validate_config(self, context, cfg, schema):
        # simple validation: type matching and key presence
        def _check(d, s, prefix=''):
            for key, rule in s.items():
                path = f"{prefix}.{key}" if prefix else key
                if isinstance(rule, dict):
                    if key not in d or not isinstance(d[key], dict):
                        raise ValueError(f"Missing key: {path}")
                    _check(d[key], rule, path)
                else:
                    if key not in d:
                        raise ValueError(f"Missing key: {path}")
                    if not isinstance(d[key], rule):
                        raise ValueError(f"Expected {rule.__name__} at {path}")
        _check(cfg, schema)
        return True

    def export_to_env(self, as_string=True, prefix=None):
        lines = []
        def _flatten(d, parent=None):
            for k, v in d.items():
                name = f"{parent}_{k}" if parent else k
                if isinstance(v, dict):
                    yield from _flatten(v, name)
                else:
                    yield name.upper(), v
        for k, v in _flatten(self.config):
            if prefix:
                key = f"{prefix}_{k}"
            else:
                key = k
            val = str(v)
            if as_string:
                lines.append(f"{key}={val}")
            else:
                logging.info(f"export {key}={val}")
                import os
                os.environ[key] = val
        return lines

    def get_namespace(self, path):
        node = self.config
        for p in path.split('.'):
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                raise KeyError(f"Namespace '{path}' not found")
        return node

    def snapshot(self):
        # return immutable snapshot
        from types import MappingProxyType
        import copy
        def _freeze(obj):
            if isinstance(obj, dict):
                return MappingProxyType({k: _freeze(v) for k, v in obj.items()})
            if isinstance(obj, list):
                return tuple(_freeze(v) for v in obj)
            return obj
        return _freeze(copy.deepcopy(self.config))

    def load_toml_source(self, path):
        try:
            import tomllib as _tl
            with open(path, 'rb') as f:
                return _tl.load(f)
        except ImportError:
            import toml as _tl
            return _tl.loads(open(path, 'r').read())

    def diff_changes(self, old, new):
        def _flatten(d, prefix=None):
            items = {}
            for k, v in d.items():
                name = f"{prefix}_{k}" if prefix else k
                if isinstance(v, dict):
                    items.update(_flatten(v, name))
                else:
                    items[name] = v
            return items
        old_flat = _flatten(old or {})
        new_flat = _flatten(new or {})
        diffs = {}
        for k in set(old_flat) | set(new_flat):
            o = old_flat.get(k)
            n = new_flat.get(k)
            if o != n:
                diffs[k] = (o, n)
        return diffs

    def override_config(self, context, override=None):
        # override full config or single key
        import copy
        if context is None:
            old = override or {}
            old_flat = self.diff_changes(self.config, override)
            self.config = copy.deepcopy(override or {})
            return old_flat
        # context is key path
        parts = context.split('.')
        node = self.config
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        old_val = node.get(parts[-1])
        node[parts[-1]] = override
        return {context.replace('.', '_'): (old_val, override)}

    def parse_cli_args(self, args):
        result = {}
        i = 0
        while i < len(args):
            arg = args[i]
            if not arg.startswith('--'):
                i += 1
                continue
            keyval = arg[2:]
            if '=' in keyval:
                key, val = keyval.split('=', 1)
            else:
                key = keyval
                val = None
                # next as value
                if i + 1 < len(args) and not args[i+1].startswith('--'):
                    val = args[i+1]
                    i += 1
                else:
                    val = 'true'
            # cast
            lv = val.lower()
            if lv == 'true': parsed = True
            elif lv == 'false': parsed = False
            else:
                try: parsed = int(val)
                except: 
                    try: parsed = float(val)
                    except: parsed = val
            result[key] = parsed
            # set in config
            parts = key.split('.') if '.' in key else [key]
            node = self.config
            for p in parts[:-1]:
                node = node.setdefault(p, {})
            node[parts[-1]] = parsed
            i += 1
        return result
    
    def log_event(self, event, data=None):
        # structured logging
        try:
            payload = {'event': event}
            if data is not None:
                payload['data'] = data
            logging.info(json.dumps(payload))
        except Exception:
            pass

# module-level API
_manager = ConfigSystem()

def register_plugin(name, loader, callback):
    _manager.register_plugin(name, loader, callback)

def load_plugin(name):
    return _manager.load_plugin(name)

def validate_config(context, cfg, schema):
    return _manager.validate_config(context, cfg, schema)

def export_to_env(as_string=True, prefix=None):
    return _manager.export_to_env(as_string, prefix)

def get_namespace(path):
    return _manager.get_namespace(path)

def snapshot():
    return _manager.snapshot()

def load_toml_source(path):
    return _manager.load_toml_source(path)

def diff_changes(old, new):
    return _manager.diff_changes(old, new)

def override_config(context, override=None):
    return _manager.override_config(context, override)

def parse_cli_args(args):
    return _manager.parse_cli_args(args)

def log_event(event, data=None):
    # delegate to manager
    return _manager.log_event(event, data)
import os
import copy
import argparse
import logging
import json
import types
try:
    import tomllib
except ImportError:
    import toml as tomllib

class ConfigManager:
    def __init__(self):
        self._config = {}
        self._plugins = {}
        self._callbacks = {}
        self._schemas = {}
        self.logger = logging.getLogger('config_system')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def register_plugin(self, name, loader, callback=None):
        self._plugins[name] = loader
        if callback:
            self._callbacks[name] = callback
        self.log_event('register_plugin', {'name': name})

    def load_plugin(self, name):
        if name not in self._plugins:
            raise KeyError(f"Plugin {name} not registered")
        new_conf = self._plugins[name]()
        old_conf = copy.deepcopy(self._config)
        self._merge_dict(self._config, new_conf)
        changes = self.diff_changes(old_conf, self._config)
        self.log_event('plugin_loaded', {'name': name, 'changes': changes})
        if name in self._callbacks:
            self._callbacks[name](self._config)
        return new_conf

    def _merge_dict(self, base, update):
        for k, v in update.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                self._merge_dict(base[k], v)
            else:
                base[k] = v

    def validate_config(self, namespace, config=None, schema=None):
        if namespace and namespace in self._schemas and schema is None:
            schema = self._schemas[namespace]
        if schema is None:
            raise KeyError(f"No schema for namespace {namespace}")
        if config is None:
            config = self.get_namespace(namespace)
        self._validate_recursive(config, schema)
        self._schemas[namespace] = schema
        self.log_event('validate_config', {'namespace': namespace})
        return True

    def _validate_recursive(self, config, schema, path=''):
        if isinstance(schema, dict):
            if not isinstance(config, dict):
                raise ValueError(f"Expected dict at {path or 'root'}")
            for key, subschema in schema.items():
                if key not in config:
                    raise ValueError(f"Missing key {path+key}")
                self._validate_recursive(config[key], subschema, path+key+'.')
        elif isinstance(schema, type):
            if not isinstance(config, schema):
                raise ValueError(f"Expected {schema} at {path[:-1]}, got {type(config)}")
        else:
            raise ValueError(f"Invalid schema at {path[:-1]}")

    def export_to_env(self, as_string=False, prefix=None):
        flat = self._flatten_dict(self._config)
        lines = []
        for k, v in flat.items():
            key = (prefix + '_' if prefix else '') + k.upper()
            val = str(v)
            if as_string:
                lines.append(f"{key}={val}")
            else:
                os.environ[key] = val
        return lines if as_string else None

    def _flatten_dict(self, d, parent_key=''):
        items = {}
        for k, v in d.items():
            new_key = parent_key + '_' + k if parent_key else k
            if isinstance(v, dict):
                items.update(self._flatten_dict(v, new_key))
            else:
                items[new_key] = v
        return items

    def log_event(self, event_type, data):
        entry = {'event': event_type, 'data': data}
        self.logger.info(json.dumps(entry))

    def get_namespace(self, namespace):
        parts = namespace.split('.')
        cur = self._config
        for p in parts:
            if not isinstance(cur, dict) or p not in cur:
                raise KeyError(f"Namespace {namespace} not found")
            cur = cur[p]
        return cur

    def snapshot(self):
        """
        Returns a deeply immutable snapshot of the current configuration.
        Nested dicts are MappingProxyType and lists are tuples.
        """
        def _freeze(obj):
            if isinstance(obj, dict):
                # freeze each value and wrap in a mapping proxy
                frozen = {k: _freeze(v) for k, v in obj.items()}
                return types.MappingProxyType(frozen)
            elif isinstance(obj, list):
                # convert lists to tuples of frozen elements
                return tuple(_freeze(v) for v in obj)
            else:
                return obj

        snap = copy.deepcopy(self._config)
        return _freeze(snap)

    def load_toml_source(self, path):
        with open(path, 'rb') as f:
            data = tomllib.load(f)
        return data

    def diff_changes(self, old, new):
        flat_old = self._flatten_dict(old)
        flat_new = self._flatten_dict(new)
        diffs = {}
        for k in set(flat_old.keys()) | set(flat_new.keys()):
            o = flat_old.get(k)
            n = flat_new.get(k)
            if o != n:
                diffs[k] = (o, n)
        return diffs

    def override_config(self, key_path, value):
        old_snapshot = copy.deepcopy(self._config)
        if key_path is None:
            if not isinstance(value, dict):
                raise ValueError("Full override requires a dict")
            self._config = copy.deepcopy(value)
        else:
            parts = key_path.split('.')
            cur = self._config
            for p in parts[:-1]:
                if p not in cur or not isinstance(cur[p], dict):
                    cur[p] = {}
                cur = cur[p]
            cur[parts[-1]] = value
        changes = self.diff_changes(old_snapshot, self._config)
        self.log_event('override', {'changes': changes})
        return changes

    def parse_cli_args(self, args=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--port', type=int, default=None)
        known, unknown = parser.parse_known_args(args)
        res = {}
        if known.port is not None:
            res['port'] = known.port
        for u in unknown:
            if u.startswith('--'):
                part = u.lstrip('-')
                if '=' in part:
                    key, val = part.split('=', 1)
                    if key.startswith('feature_'):
                        res[key] = self._parse_val(val)
                else:
                    key = part
                    if key.startswith('feature_'):
                        res[key] = True
        return res

    def _parse_val(self, val):
        if val.lower() in ('true', 'false'):
            return val.lower() == 'true'
        try:
            return int(val)
        except ValueError:
            return val

_manager = ConfigManager()

def register_plugin(name, loader, callback=None):
    return _manager.register_plugin(name, loader, callback)

def load_plugin(name):
    return _manager.load_plugin(name)

def validate_config(namespace, config=None, schema=None):
    return _manager.validate_config(namespace, config, schema)

def export_to_env(as_string=False, prefix=None):
    return _manager.export_to_env(as_string, prefix)

def log_event(event_type, data):
    return _manager.log_event(event_type, data)

def get_namespace(namespace):
    return _manager.get_namespace(namespace)

def snapshot():
    return _manager.snapshot()

def load_toml_source(path):
    return _manager.load_toml_source(path)

def diff_changes(old, new):
    return _manager.diff_changes(old, new)

def override_config(key_path, value):
    return _manager.override_config(key_path, value)

def parse_cli_args(args=None):
    return _manager.parse_cli_args(args)

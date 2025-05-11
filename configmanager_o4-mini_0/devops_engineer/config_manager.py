import os
import sys
import json
import yaml
import toml
import copy
import logging
from jsonschema import validate, ValidationError

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.plugins = {}
        self.logger = logging.getLogger('config_manager')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def register_plugin(self, name, loader):
        self.plugins[name] = loader

    def load_plugin(self, name, *args, **kwargs):
        if name not in self.plugins:
            raise KeyError(f"Plugin '{name}' not registered")
        result = self.plugins[name](*args, **kwargs)
        if not isinstance(result, dict):
            raise ValueError("Plugin loader must return a dict")
        self._merge_dicts(self.config, result)
        self.log_event('plugin_load', f"Loaded plugin '{name}'", data=result)
        return result

    def load_yaml_source(self, path):
        with open(path, 'r') as f:
            data = yaml.safe_load(f.read()) or {}
        self._merge_dicts(self.config, data)
        self.log_event('load_yaml', f"Loaded YAML from {path}", data=data)
        return data

    def load_json_source(self, path):
        with open(path, 'r') as f:
            data = json.load(f) or {}
        self._merge_dicts(self.config, data)
        self.log_event('load_json', f"Loaded JSON from {path}", data=data)
        return data

    def load_toml_source(self, path):
        with open(path, 'r') as f:
            data = toml.load(f) or {}
        self._merge_dicts(self.config, data)
        self.log_event('load_toml', f"Loaded TOML from {path}", data=data)
        return data

    def load_env_source(self, prefix=None):
        data = {}
        for k, v in os.environ.items():
            if prefix is None or k.startswith(prefix):
                data[k] = v
        self._merge_dicts(self.config, data)
        self.log_event('load_env', "Loaded environment variables", data={'prefix': prefix})
        return data

    def parse_cli_args(self, args=None):
        if args is None:
            args = sys.argv[1:]
        data = {}
        for arg in args:
            if arg.startswith('--'):
                pair = arg[2:]
                if '=' in pair:
                    key, val = pair.split('=', 1)
                    data[key] = self._cast_value(val)
                else:
                    data[pair] = True
        self._merge_dicts(self.config, data)
        self.log_event('parse_cli', "Parsed CLI arguments", data=data)
        return data

    def override_config(self, key_path, value):
        parts = key_path.split('.')
        d = self.config
        for p in parts[:-1]:
            if p not in d or not isinstance(d[p], dict):
                d[p] = {}
            d = d[p]
        d[parts[-1]] = value
        self.log_event('override', f"Overrode config '{key_path}'", data={'value': value})

    def validate_config(self, schema):
        try:
            validate(instance=self.config, schema=schema)
            self.log_event('validate', "Configuration validated successfully")
        except ValidationError as e:
            self.log_event('error', "Configuration validation failed", data={'error': str(e)})
            raise

    def export_to_env(self, update_os_env=False):
        items = {}
        def recurse(d, prefix=''):
            for k, v in d.items():
                new_key = f"{prefix}{k}".upper() if prefix else k.upper()
                if isinstance(v, dict):
                    recurse(v, prefix=new_key + '_')
                else:
                    items[new_key] = v
        recurse(self.config)
        lines = []
        for k, v in items.items():
            val = str(v)
            line = f"{k}={val}"
            lines.append(line)
            if update_os_env:
                os.environ[k] = val
        self.log_event('export', "Exported config to env", data={'count': len(lines)})
        return lines

    def snapshot(self):
        snap = copy.deepcopy(self.config)
        self.log_event('snapshot', "Snapshot taken")
        return snap

    def diff_changes(self, prev, curr):
        added, removed, changed = [], [], []
        def recurse(a, b, path=''):
            keys = set(a.keys()) | set(b.keys())
            for k in keys:
                pa = a.get(k, None)
                pb = b.get(k, None)
                full = f"{path}.{k}" if path else k
                if k not in a:
                    added.append(full)
                elif k not in b:
                    removed.append(full)
                else:
                    if isinstance(pa, dict) and isinstance(pb, dict):
                        recurse(pa, pb, full)
                    elif pa != pb:
                        changed.append(full)
        recurse(prev, curr)
        result = {'added': added, 'removed': removed, 'changed': changed}
        self.log_event('diff', "Computed diff", data=result)
        return result

    def get_namespace(self, namespace):
        parts = namespace.split('.')
        d = self.config
        for p in parts:
            if not isinstance(d, dict) or p not in d:
                return {}
            d = d[p]
        return copy.deepcopy(d)

    def log_event(self, event_type, message, **kwargs):
        record = {'event': event_type, 'message': message}
        if 'data' in kwargs:
            record.update(kwargs['data'] if isinstance(kwargs['data'], dict) else {'data': kwargs['data']})
        else:
            record.update(kwargs)
        self.logger.info(json.dumps(record))

    def _merge_dicts(self, base, new):
        for k, v in new.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._merge_dicts(base[k], v)
            else:
                base[k] = copy.deepcopy(v)

    def _cast_value(self, val):
        if val.lower() in ('true', 'false'):
            return val.lower() == 'true'
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val

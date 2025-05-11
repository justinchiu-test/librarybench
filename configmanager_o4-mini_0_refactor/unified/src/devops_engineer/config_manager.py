# coding: utf-8
"""
DevOps engineer configuration manager
"""
import os
import json
import logging
from .jsonschema import ValidationError
from .yaml import safe_load

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.plugins = {}

    def register_plugin(self, name, loader):
        if not callable(loader):
            raise ValueError('Plugin loader must be callable')
        self.plugins[name] = loader

    def load_plugin(self, name, *args, **kwargs):
        if name not in self.plugins:
            raise KeyError(f"Plugin '{name}' not found")
        result = self.plugins[name](*args, **kwargs)
        # merge result into config
        self._deep_merge(self.config, result)
        return result

    def load_yaml_source(self, path):
        # load YAML content
        with open(path, 'r') as f:
            text = f.read()
        data = safe_load(text)
        if isinstance(data, dict):
            self._deep_merge(self.config, data)
        return self.config

    def load_json_source(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        if isinstance(data, dict):
            self._deep_merge(self.config, data)
        return self.config

    def load_toml_source(self, path):
        # use stdlib tomllib if available, else fallback to toml module
        try:
            import tomllib as _tl
            with open(path, 'rb') as f:
                data = _tl.load(f)
        except ImportError:
            try:
                import toml as _tl
                data = _tl.loads(open(path, 'r').read())
            except Exception as e:
                raise
        if isinstance(data, dict):
            self._deep_merge(self.config, data)
        return self.config

    def load_env_source(self, prefix=None):
        result = {}
        for k, v in os.environ.items():
            if prefix is None or k.startswith(prefix):
                if prefix:
                    if not k.startswith(prefix):
                        continue
                result[k] = v
        return result

    def parse_cli_args(self, args):
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
                key = key.strip().replace('-', '_')
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
                self.config[key] = parsed
            i += 1
        return overrides

    def override_config(self, path, value):
        # path in form 'a.b.c'
        parts = path.split('.') if path else []
        node = self.config
        for p in parts[:-1]:
            if p not in node or not isinstance(node[p], dict):
                node[p] = {}
            node = node[p]
        if parts:
            node[parts[-1]] = value
        else:
            # override entire config
            self.config = value if isinstance(value, dict) else {}
        return self.config

    def validate_config(self, schema):
        # simple validation: type and required
        if schema.get('type') == 'object':
            props = schema.get('properties', {})
            for key, rule in props.items():
                expected = rule.get('type')
                val = self.config.get(key)
                if expected == 'integer' and not isinstance(val, int):
                    raise ValidationError(f"Expected integer for key {key}")
                if expected == 'string' and not isinstance(val, str):
                    raise ValidationError(f"Expected string for key {key}")
            for req in schema.get('required', []):
                if req not in self.config:
                    raise ValidationError(f"Missing required key: {req}")
        return True

    def export_to_env(self, update_os_env=False):
        pairs = []
        def flatten(d, prefix=''):
            for k, v in d.items():
                name = f"{prefix}_{k}" if prefix else k
                if isinstance(v, dict):
                    yield from flatten(v, name)
                else:
                    yield name.upper(), str(v)
        for k, v in flatten(self.config):
            line = f"{k}={v}"
            pairs.append(line)
            if update_os_env:
                os.environ[k] = v
        return pairs

    def snapshot(self):
        import copy
        return copy.deepcopy(self.config)

    def diff_changes(self, old, new):
        # returns dict with keys 'added','removed','changed'
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
        added = [k for k in new_flat if k not in old_flat]
        removed = [k for k in old_flat if k not in new_flat]
        changed = [k for k in old_flat if k in new_flat and old_flat[k] != new_flat[k]]
        return {'added': added, 'removed': removed, 'changed': changed}

    def get_namespace(self, path):
        node = self.config
        for p in path.split('.'):
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return {}
        return node

    def log_event(self, event, message, **extra):
        # structured logging
        import logging, json
        payload = {'event': event, 'message': message}
        payload.update(extra)
        # use dedicated logger for config_manager
        logger = logging.getLogger('config_manager')
        logger.info(json.dumps(payload))

    def _deep_merge(self, base, new):
        for k, v in new.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._deep_merge(base[k], v)
            else:
                base[k] = v
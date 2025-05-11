# coding: utf-8
"""
Platform architect configuration manager
"""
import os

class ConfigManager:
    def __init__(self, initial_config=None):
        self.config = initial_config.copy() if initial_config else {}
        self.plugins = {}
        self.events = []
        self.snapshots = []
        # default merge precedence: global < plugin < tenant < profile
        self._precedence = ['global', 'plugin', 'tenant', 'profile']
        self._version = 0

    def register_plugin(self, category, name, hook):
        # category -> {name: hook}
        self.plugins.setdefault(category, {})[name] = hook

    def log_event(self, event, data=None):
        # notify plugins
        for hook in self.plugins.get('alert', {}).values():
            try:
                hook({'event': event, 'data': data})
            except Exception:
                pass
        # record event
        self.events.append({'event': event})

    def validate_config(self, schema):
        # simple type and presence check
        for key, rule in schema.items():
            if isinstance(rule, dict):
                sub = self.config.get(key, {})
                if not isinstance(sub, dict):
                    raise TypeError(f"Expected dict at {key}")
                # nested
                for k2, r2 in rule.items():
                    val = sub.get(k2)
                    if not isinstance(val, r2):
                        raise TypeError(f"Type mismatch at {key}.{k2}")
            else:
                if key not in self.config:
                    raise ValueError(f"Missing key: {key}")
                if not isinstance(self.config[key], rule):
                    raise TypeError(f"Type mismatch at {key}")
        return True

    def export_to_env(self, update_os_env=False):
        lines = []
        def flatten(d, prefix=''):
            for k, v in d.items():
                name = f"{prefix}_{k}" if prefix else k
                if isinstance(v, dict):
                    yield from flatten(v, name)
                else:
                    yield name.upper(), str(v)
        for k, v in flatten(self.config):
            line = f"{k}={v}"
            lines.append(line)
            if update_os_env:
                os.environ[k] = v
        return lines

    def get_namespace(self, path):
        parts = path.split('.')
        node = self.config
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                raise KeyError(f"Namespace '{path}' not found")
        return node

    def diff_changes(self, old, new):
        # similar to other implementations
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
        added = {k: new_flat[k] for k in new_flat if k not in old_flat}
        removed = {k: old_flat[k] for k in old_flat if k not in new_flat}
        changed = {k: {'old': old_flat[k], 'new': new_flat[k]}
                   for k in old_flat if k in new_flat and old_flat[k] != new_flat[k]}
        return {'added': added, 'removed': removed, 'changed': changed}

    def snapshot(self):
        # record snapshot event and data
        snap = {'config': self.config.copy(), 'version': self._version}
        # record snapshot event
        self.events.append({'event': 'snapshot'})
        self.snapshots.append(snap)
        return snap

    def load_json_source(self, path):
        import json
        with open(path, 'r') as f:
            data = json.load(f)
        # merge incoming JSON data
        for k, v in data.items():
            if isinstance(v, dict) and k in self.config and isinstance(self.config[k], dict):
                self.config[k].update(v)
            else:
                self.config[k] = v
        # apply loader plugins if any
        for hook in self.plugins.get('loader', {}).values():
            try:
                result = hook(self.config)
                if isinstance(result, dict):
                    self.config = result
            except Exception:
                pass
        # notify and snapshot
        self.log_event('config_loaded', None)
        self._version += 1
        self.snapshot()

    def load_toml_source(self, path):
        try:
            import tomllib as _tl
            with open(path, 'rb') as f:
                data = _tl.load(f)
        except ImportError:
            import platform_architect.toml as _tl
            data = _tl.loads(open(path, 'r').read())
        # merge similar to JSON
        for k, v in data.items():
            if isinstance(v, dict) and k in self.config and isinstance(self.config[k], dict):
                self.config[k].update(v)
            else:
                self.config[k] = v
        self.log_event('config_loaded', None)
        self._version += 1
        self.snapshot()

    def load_env_source(self, prefix):
        for k, v in os.environ.items():
            if k.startswith(prefix):
                key = k[len(prefix):]
                self.config[key] = v

    def override_config(self, path, value):
        parts = path.split('.')
        node = self.config
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = value
        # record override event and snapshot
        self.log_event('override', None)
        self._version += 1
        self.snapshot()

    def parse_cli_args(self, args):
        # parse command-line arguments with error handling
        i = 0
        while i < len(args):
            arg = args[i]
            if not arg.startswith('--'):
                i += 1
                continue
            keyval = arg[2:]
            # parse key and value
            if '=' in keyval:
                key, val = keyval.split('=', 1)
            else:
                # expect next element as value
                if i + 1 < len(args) and not args[i+1].startswith('--'):
                    key = keyval
                    val = args[i+1]
                    i += 1
                else:
                    # malformed argument
                    self.events.append({'event': 'cli_parse_error'})
                    i += 1
                    continue
            # cast value
            lv = val.lower()
            if lv == 'true':
                parsed = True
            elif lv == 'false':
                parsed = False
            else:
                try:
                    parsed = int(val)
                except ValueError:
                    try:
                        parsed = float(val)
                    except ValueError:
                        parsed = val
            # assign to config
            if '.' in key:
                parts = key.split('.')
                node = self.config
                for p in parts[:-1]:
                    node = node.setdefault(p, {})
                node[parts[-1]] = parsed
            else:
                self.config[key] = parsed
            i += 1
        return self.config
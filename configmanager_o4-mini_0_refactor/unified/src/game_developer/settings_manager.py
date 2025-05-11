# coding: utf-8
"""
Game developer settings manager
"""
import os
import json
import logging
import re

try:
    import yaml
except ImportError:
    yaml = None

class SettingsManager:
    def __init__(self):
        self.config = {}
        self.validation_hooks = {}
        self._lazy_loaders = {}
        self.logger = None

    def namespace(self, path):
        parts = path.split('.')
        node = self.config
        for p in parts:
            if p not in node or not isinstance(node[p], dict):
                node[p] = {}
            node = node[p]

    def set(self, path, value):
        # validation hook
        if path in self.validation_hooks:
            ok = self.validation_hooks[path](value)
            if not ok:
                raise ValueError(f"Validation failed for {path}")
        parts = path.split('.')
        node = self.config
        for p in parts[:-1]:
            if p not in node or not isinstance(node[p], dict):
                node[p] = {}
            node = node[p]
        node[parts[-1]] = value
        # invalidate cache on config change
        if hasattr(self, '_cache_valid'):
            for cname in list(self._cache_valid.keys()):
                self._cache_valid[cname] = False

    def get(self, path):
        # trigger lazy load if defined for this path
        if path in self._lazy_loaders:
            # load, set, and remove loader
            val = self._lazy_loaders[path]()
            self.set(path, val)
            del self._lazy_loaders[path]
        parts = path.split('.')
        node = self.config
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                raise KeyError(f"Key '{path}' not found")
        return node

    def add_validation_hook(self, path, hook=None, **kwargs):
        if hook:
            self.validation_hooks[path] = hook
        else:
            # support min_val, max_val, pattern
            min_val = kwargs.get('min_val')
            max_val = kwargs.get('max_val')
            pattern = kwargs.get('pattern')
            def v(val):
                if min_val is not None and val < min_val:
                    return False
                if max_val is not None and val > max_val:
                    return False
                if pattern is not None and not re.match(pattern, str(val)):
                    return False
                return True
            self.validation_hooks[path] = v

    def export_to_json(self):
        return json.dumps(self.config)

    def hot_reload(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            # merge or replace
            self.config = data
            return data
        except Exception:
            raise

    def load_yaml(self, file_path):
        if yaml is None:
            raise ImportError('PyYAML is required')
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            # merge
            self.config.update(data)
        return data

    def load_envvars(self, prefix):
        for k, v in os.environ.items():
            if not k.startswith(prefix):
                continue
            tail = k[len(prefix):].lstrip('_')
            parts = tail.lower().split('_')
            # cast
            val = v
            lv = v.lower()
            if lv == 'true':
                val = True
            elif lv == 'false':
                val = False
            else:
                try:
                    val = int(v)
                except ValueError:
                    try:
                        val = float(v)
                    except ValueError:
                        val = v
            # set nested
            path = '.'.join(parts)
            self.set(path, val)

    def enable_cache(self, name, loader):
        # simple cache with invalidation on set
        if not hasattr(self, '_cache'):  # initialize
            self._cache = {}
            self._cache_loaders = {}
            self._cache_valid = {}
        self._cache_loaders[name] = loader
        self._cache_valid[name] = False

    def get_cache(self, name):
        if not getattr(self, '_cache_valid', {}).get(name, False):
            val = self._cache_loaders[name]()
            self._cache[name] = val
            self._cache_valid[name] = True
        return self._cache[name]

    def lazy_load(self, path, loader):
        self._lazy_loaders[path] = loader

    def __getattr__(self, name):
        # support lazy_load attributes
        if '_lazy_loaders' in self.__dict__ and name in self._lazy_loaders:
            val = self._lazy_loaders[name]()
            # store in config
            self.set(name, val)
            # remove loader
            del self._lazy_loaders[name]
            return val
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

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
                    if i + 1 < len(args) and not args[i+1].startswith('-'):
                        val = args[i+1]
                        i += 1
                    else:
                        val = 'true'
                # allow nested keys via '.'
                k = key
                # cast
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
                overrides[k] = parsed
                self.set(k, parsed)
            i += 1
        return overrides

    def setup_logging(self, level=logging.INFO, handler=None):
        self.logger = logging.getLogger('settings_manager')
        self.logger.setLevel(level)
        if handler:
            handler.setLevel(level)
            self.logger.addHandler(handler)
        return self.logger
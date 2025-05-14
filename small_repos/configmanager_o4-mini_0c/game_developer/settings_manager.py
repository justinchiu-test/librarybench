import os
import json
import logging
import argparse

# Try to import PyYAML; if not present, we'll provide a minimal fallback
try:
    import yaml
except ImportError:
    yaml = None

# If no real PyYAML, define a simple safe_load for basic YAML structures
if yaml is None:
    class _DummyYAML:
        @staticmethod
        def safe_load(f):
            # f may be a file handle or a string
            text = f.read() if hasattr(f, 'read') else str(f)
            lines = text.splitlines()
            result = {}
            stack = [(-1, result)]
            for line in lines:
                raw = line.rstrip()
                if not raw or raw.lstrip().startswith('#'):
                    continue
                indent = len(raw) - len(raw.lstrip(' '))
                stripped = raw.lstrip()
                # New mapping start
                if stripped.endswith(':'):
                    key = stripped[:-1]
                    # find appropriate parent based on indent
                    while stack and stack[-1][0] >= indent:
                        stack.pop()
                    parent = stack[-1][1]
                    parent[key] = {}
                    stack.append((indent, parent[key]))
                else:
                    if ':' in stripped:
                        key, val_str = stripped.split(':', 1)
                        val_str = val_str.strip()
                        # try to cast
                        low = val_str.lower()
                        if low in ('true', 'false'):
                            val = (low == 'true')
                        else:
                            try:
                                if '.' in val_str:
                                    val = float(val_str)
                                else:
                                    val = int(val_str)
                            except Exception:
                                val = val_str
                        # find correct parent
                        while stack and stack[-1][0] >= indent:
                            stack.pop()
                        stack[-1][1][key] = val
            return result
    yaml = _DummyYAML()

class SettingsManager:
    def __init__(self):
        self.config = {}
        self.validation_hooks = []  # list of (path, func)
        self.logger = logging.getLogger('SettingsManager')
        self.cache_store = {}
        self.cache_loaders = {}
        self.lazy_loaders = {}

    def namespace(self, path):
        parts = path.split('.')
        d = self.config
        for p in parts:
            if p not in d or not isinstance(d[p], dict):
                d[p] = {}
            d = d[p]
        self.logger.debug(f"Namespace created: {path}")

    def add_validation_hook(self, path, func):
        self.validation_hooks.append((path, func))

    def _run_validation(self, path, value):
        for hook_path, func in self.validation_hooks:
            if hook_path == path:
                if not func(value):
                    msg = f"Validation failed for {path}: {value}"
                    self.logger.error(msg)
                    raise ValueError(msg)

    def set(self, path, value):
        parts = path.split('.')
        d = self.config
        for p in parts[:-1]:
            if p not in d or not isinstance(d[p], dict):
                d[p] = {}
            d = d[p]
        key = parts[-1]
        self._run_validation(path, value)
        d[key] = value
        self.logger.info(f"Set {path} = {value}")
        # Invalidate cache on any set
        self.cache_store.clear()

    def get(self, path):
        # First, check for lazy loader
        if path in self.lazy_loaders:
            loader = self.lazy_loaders.pop(path)
            val = loader()
            # store the loaded value
            self.set(path, val)
            return val

        # Then traverse the config tree
        parts = path.split('.')
        d = self.config
        for p in parts:
            if p not in d:
                return None
            d = d[p]
        return d

    def hot_reload(self, *file_paths):
        for fp in file_paths:
            if fp.endswith('.json'):
                with open(fp) as f:
                    data = json.load(f)
            elif fp.endswith(('.yml', '.yaml')):
                data = self.load_yaml(fp)
            else:
                continue
            self._deep_merge(self.config, data)
            self.logger.info(f"Hot-reloaded {fp}")

    def _deep_merge(self, base, new):
        for k, v in new.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._deep_merge(base[k], v)
            else:
                base[k] = v

    def export_to_json(self):
        return json.dumps(self.config)

    def setup_logging(self, level=logging.INFO, handler=None):
        self.logger.setLevel(level)
        if handler:
            self.logger.addHandler(handler)
        else:
            ch = logging.StreamHandler()
            ch.setLevel(level)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def load_yaml(self, file_path):
        # Honors module-level yaml variable, so monkeypatching yaml=None triggers ImportError
        if yaml is None:
            raise ImportError("PyYAML is not installed")
        with open(file_path) as f:
            return yaml.safe_load(f) or {}

    def load_envvars(self, prefix='', types_map=None):
        for k, v in os.environ.items():
            if prefix and not k.startswith(prefix):
                continue
            # strip the prefix
            key = k[len(prefix):] if prefix else k
            # drop any leading underscores after prefix removal
            key = key.lstrip('_')
            # map underscores to nested path separator
            path = key.lower().replace('_', '.')
            # get cast type if provided
            caster = types_map.get(key) if types_map else None
            val = self._cast_value(v, caster)
            self.set(path, val)

    def _cast_value(self, val, to_type=None):
        if to_type:
            return to_type(val)
        low = val.lower()
        if low in ('true', 'false'):
            return low == 'true'
        try:
            if '.' in val:
                return float(val)
            return int(val)
        except Exception:
            return val

    def enable_cache(self, key, loader_func):
        self.cache_loaders[key] = loader_func

    def get_cache(self, key):
        if key in self.cache_store:
            return self.cache_store[key]
        if key in self.cache_loaders:
            val = self.cache_loaders[key]()
            self.cache_store[key] = val
            return val
        return None

    def parse_cli_args(self, args=None):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('rest', nargs='*')
        parsed, unknown = parser.parse_known_args(args)
        for arg in unknown:
            if arg.startswith('--') and '=' in arg:
                k, v = arg[2:].split('=', 1)
                self.set(k, self._cast_value(v))

    def lazy_load(self, path, loader_func):
        self.lazy_loaders[path] = loader_func

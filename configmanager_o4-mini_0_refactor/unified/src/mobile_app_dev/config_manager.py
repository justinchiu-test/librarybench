# coding: utf-8
"""
Mobile app developer configuration manager
"""
import os
import sys
import json
import threading
import time

try:
    import yaml
except ImportError:
    yaml = None

class ConfigManager:
    def __init__(self):
        self._config = {}
        self._current_ns = []
        self.logger = None
        self._cache = {}
        # validation rules storage
        self.validation_rules = {}

    def setup_logging(self):
        if self.logger:
            return self.logger
        import logging
        self.logger = logging.getLogger('mobile_app_dev')
        return self.logger

    def _set(self, key, value):
        node = self._config
        for ns in self._current_ns:
            node = node.setdefault(ns, {})
        node[key] = value

    def _get(self, key):
        node = self._config
        for ns in self._current_ns:
            node = node.get(ns, {})
        return node.get(key)

    def namespace(self, path):
        # context manager for namespace setting
        parts = path.split('.')
        manager = self
        class _NamespaceCtx:
            def __init__(self):
                self.prev = list(manager._current_ns)
                self.ns_parts = parts
            def __enter__(self_inner):
                manager._current_ns = self_inner.ns_parts
                # ensure namespace exists
                node = manager._config
                for p in self_inner.ns_parts:
                    node = node.setdefault(p, {})
                return manager
            def __exit__(self_inner, exc_type, exc, tb):
                manager._current_ns = self_inner.prev
        return _NamespaceCtx()

    def load_yaml(self, file_path):
        if yaml is None:
            raise ImportError('yaml library not available')
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            for k, v in data.items():
                self._set(k, v)
        return data

    def load_envvars(self, prefix):
        result = {}
        for k, v in os.environ.items():
            if not k.startswith(prefix):
                continue
            # cast
            lv = v.lower()
            if lv == 'true':
                parsed = True
            elif lv == 'false':
                parsed = False
            else:
                try:
                    parsed = int(v)
                except ValueError:
                    try:
                        parsed = float(v)
                    except ValueError:
                        parsed = v
            result[k] = parsed
        return result

    def parse_cli_args(self):
        args = sys.argv[1:]
        result = {}
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
                result[key] = parsed
                self._set(key, parsed)
            i += 1
        return result

    def add_validation_hook(self, path, min_val=None, max_val=None, pattern=None):
        # add numeric or pattern validation for a key; reset previous hooks
        self.validation_rules.clear()
        self.validation_rules[path] = (min_val, max_val, pattern)

    def validate(self):
        import re
        for path, (min_val, max_val, pattern) in getattr(self, 'validation_rules', {}).items():
            val = self._get(path)
            if val is None:
                continue
            if min_val is not None and val < min_val:
                raise ValueError(f"Validation failed for {path}")
            if max_val is not None and val > max_val:
                raise ValueError(f"Validation failed for {path}")
            if pattern is not None and not re.match(pattern, str(val)):
                raise ValueError(f"Validation failed for {path}")
        return True

    def export_to_json(self):
        return json.dumps(self._config)

    def enable_cache(self, name, loader):
        if name not in self._cache:
            self._cache[name] = loader()
        return self._cache[name]

    def lazy_load(self, path, loader):
        # register lazy loader for a key
        if '_lazy' not in self.__dict__:
            self._lazy = {}
        self._lazy[path] = loader

    def __getattr__(self, name):
        lazy_store = self.__dict__.get('_lazy', {})
        if name in lazy_store:
            val = lazy_store[name]()
            # store
            self._set(name, val)
            # remove loader
            del self._lazy[name]
            return val
        # check if the name exists in current namespace config
        val = self._get(name)
        if val is not None:
            return val
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def hot_reload(self, file_path, callback, interval=1.0):
        stop_event = threading.Event()
        def watch():
            try:
                last = os.path.getmtime(file_path)
            except Exception:
                last = None
            while not stop_event.is_set():
                try:
                    m = os.path.getmtime(file_path)
                except Exception:
                    m = None
                if last is None:
                    last = m
                elif m is not None and m != last:
                    last = m
                    callback(file_path)
                time.sleep(interval)
        t = threading.Thread(target=watch, daemon=True)
        t.start()
        class Handle:
            def stop(self_inner):
                stop_event.set()
                t.join()
        return Handle()
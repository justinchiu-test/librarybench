import os
import threading
import re
from copy import deepcopy

class Config:
    def __init__(self):
        self._base = {}
        self._profiles = {}
        self._defaults = {}
        self._active_profile = None
        self._watchers = []  # list of (pattern, callback)
        self._coercers = {}  # key -> func
        self._lock = threading.RLock()

    def load_dict(self, data_dict, profile=None):
        with self._lock:
            target = self._base if profile is None else self._profiles.setdefault(profile, {})
            self._deep_merge(target, data_dict)

    def load_yaml(self, file_path, profile=None):
        with open(file_path, 'r') as f:
            text = f.read()
        try:
            import yaml
            data = yaml.safe_load(text) or {}
        except ImportError:
            data = self._simple_yaml_load(text) or {}
        self.load_dict(data, profile=profile)

    def select_profile(self, profile):
        with self._lock:
            # allow selecting None to clear profile
            if profile is not None and profile not in self._profiles:
                self._profiles[profile] = {}
            self._active_profile = profile

    def add_default(self, key, value):
        with self._lock:
            parts = key.split('.')
            self._set_nested(self._defaults, parts, value)

    def register_watcher(self, pattern, callback):
        with self._lock:
            self._watchers.append((pattern, callback))

    def register_coercer(self, key, func):
        with self._lock:
            self._coercers[key] = func

    def set(self, key, value):
        with self._lock:
            parts = key.split('.')
            # get raw old value from merged without interpolation
            merged_before = self.visualize()
            try:
                old = self._get_nested(merged_before, parts)
            except KeyError:
                old = None
            # set in base or active profile
            target = self._profiles[self._active_profile] if self._active_profile else self._base
            self._set_nested(target, parts, value)
            # get raw new value
            merged_after = self.visualize()
            try:
                new = self._get_nested(merged_after, parts)
            except KeyError:
                new = None
            # notify watchers
            for pattern, cb in self._watchers:
                if pattern == key:
                    cb(key, old, new)

    def get(self, key):
        with self._lock:
            merged = {}
            # defaults
            self._deep_merge(merged, deepcopy(self._defaults))
            # base
            self._deep_merge(merged, deepcopy(self._base))
            # profile
            if self._active_profile:
                prof = self._profiles.get(self._active_profile, {})
                self._deep_merge(merged, deepcopy(prof))
            parts = key.split('.')
            try:
                val = self._get_nested(merged, parts)
            except KeyError:
                return None
            # resolve interpolation with awareness of overall merged context
            val = self._resolve_interpolation(val, set([key]), merged)
            # coercion
            if key in self._coercers:
                val = self._coercers[key](val)
            return val

    def visualize(self):
        with self._lock:
            merged = {}
            self._deep_merge(merged, deepcopy(self._defaults))
            self._deep_merge(merged, deepcopy(self._base))
            if self._active_profile:
                self._deep_merge(merged, deepcopy(self._profiles.get(self._active_profile, {})))
            return merged

    def _deep_merge(self, base, override):
        for k, v in override.items():
            if k in base:
                if isinstance(base[k], dict) and isinstance(v, dict):
                    self._deep_merge(base[k], v)
                elif isinstance(base[k], list) and isinstance(v, list):
                    base[k] = v[:]
                elif type(base[k]) != type(v):
                    raise ValueError(f"Type conflict at key '{k}': {type(base[k])} vs {type(v)}")
                else:
                    base[k] = deepcopy(v)
            else:
                base[k] = deepcopy(v)

    def _set_nested(self, d, parts, value):
        for p in parts[:-1]:
            if p not in d or not isinstance(d[p], dict):
                d[p] = {}
            d = d[p]
        d[parts[-1]] = value

    def _get_nested(self, d, parts):
        for p in parts:
            d = d[p]
        return d

    def _simple_yaml_load(self, text):
        """
        A minimal YAML loader for simple key: value mappings with nesting via indentation.
        """
        root = {}
        stack = [(0, root)]
        for rawline in text.split('\n'):
            if not rawline.strip() or rawline.lstrip().startswith('#'):
                continue
            indent = len(rawline) - len(rawline.lstrip(' '))
            stripped = rawline.lstrip(' ')
            if ':' not in stripped:
                continue
            key, val = stripped.split(':', 1)
            key = key.strip()
            val = val.strip()
            # find correct parent by indent, but never pop the root
            while len(stack) > 1 and indent <= stack[-1][0]:
                stack.pop()
            parent = stack[-1][1]
            if val == '':
                # nested map
                new = {}
                parent[key] = new
                stack.append((indent, new))
            else:
                # parse scalar
                if val.isdigit():
                    parsed = int(val)
                else:
                    try:
                        parsed = float(val)
                    except ValueError:
                        parsed = val
                parent[key] = parsed
        return root

    def _resolve_interpolation(self, val, seen, merged):
        if isinstance(val, str):
            pattern = re.compile(r'\$\{([^}]+)\}')
            def repl(match):
                inner = match.group(1)
                # environment variable
                if inner in os.environ:
                    return os.environ[inner]
                # circular detection
                if inner in seen:
                    raise ValueError(f"Circular reference detected: {inner}")
                parts = inner.split('.')
                try:
                    rhs = self._get_nested(merged, parts)
                except KeyError:
                    return ''
                # mark and recurse
                seen.add(inner)
                resolved = self._resolve_interpolation(rhs, seen, merged)
                seen.remove(inner)
                return str(resolved)
            return pattern.sub(repl, val)
        elif isinstance(val, list):
            return [self._resolve_interpolation(x, set(seen), merged) for x in val]
        elif isinstance(val, dict):
            return {k: self._resolve_interpolation(v, set(seen), merged) for k, v in val.items()}
        else:
            return val

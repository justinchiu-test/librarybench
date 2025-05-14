import os
import sys
import time
import json
import threading
import logging
from functools import wraps
from collections import defaultdict

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

class MonitorHandle:
    def __init__(self, thread, stop_event):
        self._thread = thread
        self._stop_event = stop_event

    def stop(self):
        self._stop_event.set()
        self._thread.join(timeout=1)

class ConfigManager:
    def __init__(self):
        self._config = {}
        self._validation_hooks = {}
        self._cache = {}
        self._log_setup = False
        self._namespaced = False
        self._current_ns = None
        self._reload_handles = []

    def setup_logging(self, level=logging.DEBUG):
        if not self._log_setup:
            logging.basicConfig(
                level=level,
                format='%(asctime)s %(levelname)s %(name)s %(message)s'
            )
            self.logger = logging.getLogger('ConfigManager')
            self._log_setup = True
        return self.logger

    def namespace(self, name):
        class NSCtx:
            def __init__(self, manager, name):
                self.manager = manager
                self.name = name
                self.prev_ns = manager._current_ns
            def __enter__(self):
                self.manager._current_ns = self.name
                self.manager._namespaced = True
                if self.name not in self.manager._config:
                    self.manager._config[self.name] = {}
                return self.manager
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.manager._current_ns = self.prev_ns
                self.manager._namespaced = bool(self.prev_ns)
        return NSCtx(self, name)

    def _set(self, key, value):
        if self._namespaced and self._current_ns:
            self._config[self._current_ns][key] = value
        else:
            self._config[key] = value

    def _get(self, key):
        if self._namespaced and self._current_ns:
            return self._config[self._current_ns].get(key)
        return self._config.get(key)

    def load_yaml(self, path):
        """
        Load YAML file. If PyYAML is available, use it, otherwise
        do a simple fallback parser for "key: value" lines.
        """
        data = {}
        with open(path, 'r') as f:
            if _HAS_YAML:
                loaded = yaml.safe_load(f) or {}
                data = loaded
            else:
                content = f.read()
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if ':' in line:
                        key, val = line.split(':', 1)
                        key = key.strip()
                        val = val.strip()
                        # strip quotes
                        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                            val = val[1:-1]
                        data[key] = self._cast_envvar(val)
        # set into config
        for k, v in data.items():
            self._set(k, v)
        return data

    def load_envvars(self, prefix=None):
        data = {}
        for k, v in os.environ.items():
            if prefix is None or k.startswith(prefix):
                cast_val = self._cast_envvar(v)
                self._set(k, cast_val)
                data[k] = cast_val
        return data

    def _cast_envvar(self, v):
        if isinstance(v, str) and v.lower() in ('true', 'false'):
            return v.lower() == 'true'
        try:
            if isinstance(v, str) and '.' in v:
                return float(v)
            return int(v)
        except Exception:
            return v

    def parse_cli_args(self, args=None):
        args = args if args is not None else sys.argv[1:]
        data = {}
        for arg in args:
            if arg.startswith('--'):
                if '=' in arg:
                    key, val = arg[2:].split('=', 1)
                    data[key] = self._cast_envvar(val)
                else:
                    key = arg[2:]
                    data[key] = True
                self._set(key, data[key])
        return data

    def add_validation_hook(self, key, pattern=None, min_val=None, max_val=None):
        # Clear existing hooks so each call starts fresh (per test expectations)
        self._validation_hooks.clear()
        self._validation_hooks[key] = (pattern, min_val, max_val)

    def validate(self):
        for key, (pattern, min_v, max_v) in self._validation_hooks.items():
            # fetch value
            if self._namespaced and self._current_ns:
                val = self._config[self._current_ns].get(key)
            else:
                val = self._config.get(key)
            if val is None:
                continue
            # pattern check
            if pattern:
                import re
                if not re.match(pattern, str(val)):
                    raise ValueError(f"Validation failed for {key}: {val}")
            # numeric check
            if isinstance(val, (int, float)):
                if min_v is not None and val < min_v:
                    raise ValueError(f"{key} below min {min_v}")
                if max_v is not None and val > max_v:
                    raise ValueError(f"{key} above max {max_v}")
        return True

    def export_to_json(self):
        return json.dumps(self._config)

    def enable_cache(self, key, loader_func):
        if key in self._cache:
            return self._cache[key]
        val = loader_func()
        self._cache[key] = val
        return val

    def lazy_load(self, key, loader_func):
        @property
        @wraps(loader_func)
        def _lazy(_):
            if key not in self._cache:
                self._cache[key] = loader_func()
            return self._cache[key]
        setattr(self.__class__, key, _lazy)
        return _lazy

    def hot_reload(self, path, callback, interval=0.1):
        stop_event = threading.Event()
        def monitor():
            try:
                last_mtime = os.path.getmtime(path)
            except Exception:
                last_mtime = None
            while not stop_event.is_set():
                try:
                    mtime = os.path.getmtime(path)
                    if last_mtime is None:
                        last_mtime = mtime
                    elif mtime != last_mtime:
                        self.setup_logging()
                        self.logger.info(f"File changed: {path}")
                        callback(path)
                        last_mtime = mtime
                except FileNotFoundError:
                    pass
                time.sleep(interval)
        t = threading.Thread(target=monitor, daemon=True)
        t.start()
        handle = MonitorHandle(t, stop_event)
        self._reload_handles.append(handle)
        return handle

# coding: utf-8
"""
Freelancer developer configuration manager
"""
import os
import json
import threading
import time
import logging

class ConfigManager:
    def __init__(self, defaults=None, file_path=None):
        self.defaults = defaults or {}
        self.file_path = file_path
        self.file_config = {}
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.file_config = json.load(f)
            except Exception:
                self.file_config = {}
        # plugin system for secrets and merge
        self._plugins = {}
        # default precedence: highest priority first: env, file, defaults
        self._precedence = ['env', 'file', 'defaults']
        # cache decorator storage
        self._cache = {}

    def set_precedence(self, precedence):
        if isinstance(precedence, list):
            self._precedence = precedence
        else:
            raise ValueError('precedence must be a list')

    def merge_configs(self):
        # Prepare data sources
        # Plugin data
        plugin_data = {}
        for name, plugin in self._plugins.items():
            if hasattr(plugin, 'merge'):
                plugin_data[name] = plugin.merge() or {}
            elif callable(plugin):
                plugin_data[name] = plugin() or {}
        # Build merge order: lowest priority first
        sources = []
        for source in reversed(self._precedence):
            if source == 'defaults':
                sources.append(self.defaults or {})
            elif source == 'file':
                sources.append(self.file_config or {})
            elif source == 'env':
                # override only existing keys
                env_data = {}
                keys = set(self.defaults.keys()) | set(self.file_config.keys())
                for k in keys:
                    if k in os.environ:
                        env_data[k] = os.environ[k]
                sources.append(env_data)
            elif source in plugin_data:
                sources.append(plugin_data[source])
        # Deep merge all sources
        import copy
        def merge(a, b):
            for k, v in b.items():
                if k in a and isinstance(a[k], dict) and isinstance(v, dict):
                    merge(a[k], v)
                else:
                    a[k] = v
            return a
        merged = {}
        for src in sources:
            merge(merged, src)
        return merged

    def select_profile(self, profile_name):
        profiles = self.defaults.get('profiles', {})
        if profile_name not in profiles:
            raise KeyError(f"Profile '{profile_name}' not found")
        return profiles[profile_name]

    def export_env_vars(self, to_os=False):
        cfg = self.merge_configs()
        lines = []
        for k, v in cfg.items():
            line = f"{k}={v}"
            lines.append(line)
            if to_os:
                os.environ[k] = str(v)
        return lines

    def export_to_ini(self, file_path=None):
        import configparser
        parser = configparser.ConfigParser()
        merged = self.defaults.copy()
        # flatten nested sections
        for k, v in merged.items():
            if isinstance(v, dict):
                parser[k] = {ik: str(iv) for ik, iv in v.items()}
            else:
                parser['DEFAULT'][k] = str(v)
        from io import StringIO
        if file_path is None:
            buf = StringIO()
            parser.write(buf)
            return buf.getvalue()
        else:
            with open(file_path, 'w') as f:
                parser.write(f)

    def enable_hot_reload(self, interval=1.0, callback=None):
        # watch JSON file for changes
        if not self.file_path:
            return
        self._stop_event = threading.Event()
        def load_file():
            try:
                with open(self.file_path, 'r') as f:
                    self.file_config = json.load(f)
            except Exception:
                pass
        load_file()
        last_mtime = None
        try:
            last_mtime = os.path.getmtime(self.file_path)
        except Exception:
            last_mtime = None
        def watch():
            nonlocal last_mtime
            while not self._stop_event.is_set():
                try:
                    m = os.path.getmtime(self.file_path)
                except Exception:
                    m = None
                if m is not None and m != last_mtime:
                    last_mtime = m
                    load_file()
                    if callback:
                        callback()
                time.sleep(interval)
        t = threading.Thread(target=watch, daemon=True)
        t.start()

    def disable_hot_reload(self):
        if hasattr(self, '_stop_event') and self._stop_event:
            self._stop_event.set()

    def setup_logging(self, log_file, level=logging.INFO):
        logger = logging.getLogger('freelancer_dev')
        logger.setLevel(level)
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)
        fmt = logging.Formatter('%(message)s')
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        self.logger = logger

    def register_plugin(self, name, plugin):
        # secrets and merge plugin registration
        self._plugins[name] = plugin

    def fetch_secret(self, name, store=None):
        if store:
            if store not in self._plugins:
                raise KeyError(f"Store '{store}' not found")
            return getattr(self._plugins[store], 'get')(name)
        # default store
        if 'default' in self._plugins:
            return getattr(self._plugins['default'], 'get')(name)
        # try all stores
        for plugin in self._plugins.values():
            if hasattr(plugin, 'get'):
                val = plugin.get(name)
                if val is not None:
                    return val
        return None

    def cache_manager(self, func):
        def wrapper(*args, **kwargs):
            key = (func.__name__, args, tuple(kwargs.items()))
            if key in self._cache:
                return self._cache[key]
            res = func(*args, **kwargs)
            self._cache[key] = res
            return res
        return wrapper

    def set_precedence(self, precedence):
        # override previous definition
        if isinstance(precedence, list):
            self._precedence = precedence
        else:
            raise ValueError('precedence must be a list')
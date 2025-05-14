import os
import json
import threading
import time
import logging
import configparser
import functools

class ConfigManager:
    def __init__(self, defaults=None, file_path=None, env_prefix=None):
        self.defaults = defaults or {}
        self.file_path = file_path
        self.env_prefix = env_prefix
        self.file_config = {}
        self.env_config = {}
        self.plugins = {}
        # internal precedence is low-to-high (earlier entries are lower priority)
        self.precedence = ['defaults', 'file', 'env']
        self.logger = logging.getLogger('ConfigManager')
        self.profile = None
        self._stop_reload = False
        self._reload_thread = None
        if file_path:
            self._load_file_config()

    def _load_file_config(self):
        with open(self.file_path, 'r') as f:
            self.file_config = json.load(f)

    def set_precedence(self, precedence_list):
        """
        Accepts a precedence list in descending order (highest to lowest priority),
        but internally we store precedence as ascending (lowest to highest),
        so we reverse the provided list.
        """
        self.precedence = list(reversed(precedence_list))

    def merge_configs(self):
        self.env_config = self._load_env_vars()
        merged = {}
        for source in self.precedence:
            if source == 'defaults':
                self._deep_update(merged, self.defaults)
            elif source == 'file':
                self._deep_update(merged, self.file_config)
            elif source == 'env':
                self._deep_update(merged, self.env_config)
            else:
                plugin = self.plugins.get(source)
                if plugin and hasattr(plugin, 'merge'):
                    self._deep_update(merged, plugin.merge())
        self.logger.debug(f"Merged config: {merged}")
        return merged

    def _deep_update(self, dest, src):
        for k, v in src.items():
            if isinstance(v, dict) and isinstance(dest.get(k), dict):
                self._deep_update(dest[k], v)
            else:
                dest[k] = v

    def _load_env_vars(self):
        env = {}
        for k, v in os.environ.items():
            if self.env_prefix:
                if k.startswith(self.env_prefix):
                    env_key = k[len(self.env_prefix):]
                    env[env_key] = v
            else:
                env[k] = v
        return env

    def select_profile(self, profile_name):
        cfg = self.merge_configs()
        profiles = cfg.get('profiles', {})
        if profile_name not in profiles:
            self.logger.error(f"Profile {profile_name} not found")
            raise KeyError(f"Profile {profile_name} not found")
        self.profile = profile_name
        return profiles[profile_name]

    def export_env_vars(self, to_os=False):
        cfg = self.merge_configs()
        lines = [f"{k}={v}" for k, v in cfg.items()]
        if to_os:
            for k, v in cfg.items():
                os.environ[k] = str(v)
        return lines

    def export_to_ini(self, file_path=None):
        cfg = self.merge_configs()
        cp = configparser.ConfigParser()
        for k, v in cfg.items():
            if isinstance(v, dict):
                cp[k] = {str(kk): str(vv) for kk, vv in v.items()}
            else:
                if 'DEFAULT' not in cp:
                    cp['DEFAULT'] = {}
                cp['DEFAULT'][k] = str(v)
        if file_path:
            with open(file_path, 'w') as f:
                cp.write(f)
            return None
        else:
            from io import StringIO
            s = StringIO()
            cp.write(s)
            return s.getvalue()

    def enable_hot_reload(self, interval=1, callback=None):
        def watch():
            last_mtime = None
            while not self._stop_reload:
                try:
                    mtime = os.path.getmtime(self.file_path)
                    if last_mtime is None:
                        last_mtime = mtime
                    elif mtime != last_mtime:
                        last_mtime = mtime
                        self._load_file_config()
                        if callback:
                            callback()
                except Exception:
                    pass
                time.sleep(interval)
        self._stop_reload = False
        self._reload_thread = threading.Thread(target=watch, daemon=True)
        self._reload_thread.start()

    def disable_hot_reload(self):
        self._stop_reload = True
        if self._reload_thread:
            self._reload_thread.join()

    def setup_logging(self, log_file=None, level=logging.INFO):
        self.logger.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        if log_file:
            fh = logging.FileHandler(log_file)
            fh.setLevel(level)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def fetch_secret(self, name, store='default'):
        plugin = self.plugins.get(store)
        if plugin and hasattr(plugin, 'get'):
            return plugin.get(name)
        raise KeyError(f"Secret store {store} not registered")

    def cache_manager(self, func):
        cache = {}
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            if key in cache:
                return cache[key]
            result = func(*args, **kwargs)
            cache[key] = result
            return result
        return wrapper

    def register_plugin(self, name, plugin):
        self.plugins[name] = plugin

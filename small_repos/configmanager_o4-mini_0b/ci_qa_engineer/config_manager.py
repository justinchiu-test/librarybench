import os
import threading
import time
import logging
import configparser
from functools import wraps

# Ensure 'logging' is available globally (e.g., in test modules without explicit import)
import builtins
builtins.logging = logging

def setup_logging(name='config_manager', level=logging.DEBUG):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger

class CacheManager:
    def __init__(self):
        self._cache = {}

    def get(self, key, factory):
        if key not in self._cache:
            self._cache[key] = factory()
        return self._cache[key]

class ConfigManager:
    def __init__(self):
        self.logger = setup_logging()
        self.plugins = []
        self.cache = CacheManager()
        self.precedence_rules = {}
        self._watch_thread = None
        self._watch_running = False
        self._watch_paths = []
        self._watch_callback = None
        self._watch_interval = 1.0

    def set_precedence(self, precedence_rules):
        self.precedence_rules = precedence_rules

    def register_plugin(self, plugin):
        self.plugins.append(plugin)

    def merge_configs(self, defaults, feature_flags, env_overrides):
        merged = {}
        keys = set(defaults) | set(feature_flags) | set(env_overrides)
        for key in keys:
            if key in self.precedence_rules:
                order = self.precedence_rules[key]
                for src in order:
                    if src == 'env' and key in env_overrides:
                        merged[key] = env_overrides[key]
                        break
                    if src == 'flags' and key in feature_flags:
                        merged[key] = feature_flags[key]
                        break
                    if src == 'defaults' and key in defaults:
                        merged[key] = defaults[key]
                        break
            else:
                if key in defaults:
                    merged[key] = defaults[key]
                if key in feature_flags:
                    merged[key] = feature_flags[key]
                if key in env_overrides:
                    merged[key] = env_overrides[key]
        self.logger.debug(f"Merged config: {merged}")
        for plugin in self.plugins:
            try:
                result = plugin(merged)
                if result is False:
                    self.logger.error(f"Plugin {plugin} reported validation failure")
            except Exception as e:
                self.logger.error(f"Plugin {plugin} exception: {e}")
        return merged

    def export_env_vars(self, config):
        pairs = [f"{k}={v}" for k, v in config.items()]
        return pairs

    def export_to_ini(self, config, filepath):
        parser = configparser.ConfigParser()
        parser['DEFAULT'] = {k: str(v) for k, v in config.items()}
        with open(filepath, 'w') as f:
            parser.write(f)
        self.logger.debug(f"Exported INI to {filepath}")

    def select_profile(self, base_config, profile_overrides):
        for profile, overrides in profile_overrides.items():
            cfg = base_config.copy()
            cfg.update(overrides)
            cfg['profile'] = profile
            yield cfg

    def fetch_secret(self, name, sources):
        for src in sources:
            try:
                val = src.get(name)
            except Exception:
                val = None
            if val is not None:
                self.logger.debug(f"Fetched secret '{name}' from {src}")
                return val
        self.logger.error(f"Secret '{name}' not found in sources")
        return None

    def enable_hot_reload(self, paths, callback, poll_interval=1.0):
        if self._watch_running:
            return
        self._watch_paths = list(paths)
        self._watch_callback = callback
        self._watch_interval = poll_interval
        self._mtimes = {}
        for p in self._watch_paths:
            try:
                self._mtimes[p] = os.path.getmtime(p)
            except Exception:
                self._mtimes[p] = None
        self._watch_running = True

        def _watch():
            while self._watch_running:
                time.sleep(self._watch_interval)
                for p in self._watch_paths:
                    try:
                        m = os.path.getmtime(p)
                    except Exception:
                        m = None
                    if self._mtimes.get(p) != m:
                        self._mtimes[p] = m
                        try:
                            callback(p)
                            self.logger.debug(f"Reload event for {p}")
                        except Exception as e:
                            self.logger.error(f"Hot-reload callback error: {e}")

        self._watch_thread = threading.Thread(target=_watch, daemon=True)
        self._watch_thread.start()

    def stop_hot_reload(self):
        if self._watch_running:
            self._watch_running = False
            if self._watch_thread:
                self._watch_thread.join(timeout=2.0)

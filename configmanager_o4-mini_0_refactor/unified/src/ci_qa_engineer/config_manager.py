# coding: utf-8
"""
ci_qa_engineer configuration manager module
"""
import os
import threading
import time
import logging
import configparser

class CacheManager:
    def __init__(self):
        self._cache = {}
    def get(self, key, factory):
        if key not in self._cache:
            self._cache[key] = factory()
        return self._cache[key]

def setup_logging(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger

class ConfigManager:
    def __init__(self):
        self._precedence = {}
        # default precedence: highest priority first
        self._default_precedence = ['env', 'flags', 'defaults']
        self.plugins = []
        self._watch_thread = None
        self._stop_event = None

    def set_precedence(self, precedence):
        # precedence: dict mapping key -> list of source names
        if isinstance(precedence, dict):
            self._precedence = precedence
        else:
            raise ValueError('precedence must be a dict')

    def merge_configs(self, defaults, flags, env):
        merged = {}
        # collect all keys
        keys = set()
        if defaults:
            keys.update(defaults.keys())
        if flags:
            keys.update(flags.keys())
        if env:
            keys.update(env.keys())
        for key in keys:
            order = self._precedence.get(key, self._default_precedence)
            for source in order:
                if source == 'defaults' and defaults and key in defaults:
                    merged[key] = defaults[key]
                    break
                if source == 'flags' and flags and key in flags:
                    merged[key] = flags[key]
                    break
                if source == 'env' and env and key in env:
                    merged[key] = env[key]
                    break
        # run plugins
        for plugin in self.plugins:
            try:
                plugin(merged)
            except Exception as e:
                logging.error('validation failure', exc_info=e)
        return merged

    def export_env_vars(self, cfg):
        pairs = []
        for k, v in cfg.items():
            pairs.append(f"{k}={v}")
        return pairs

    def export_to_ini(self, cfg, file_path):
        parser = configparser.ConfigParser()
        parser['DEFAULT'] = {k: str(v) for k, v in cfg.items()}
        with open(file_path, 'w') as f:
            parser.write(f)

    def select_profile(self, base, overrides):
        # base: dict, overrides: dict of profile_name -> override dict
        for profile, override in overrides.items():
            cfg = dict(base) if base else {}
            cfg.update(override or {})
            cfg['profile'] = profile
            yield cfg

    def register_plugin(self, plugin):
        if not callable(plugin):
            raise ValueError('plugin must be callable')
        self.plugins.append(plugin)

    def fetch_secret(self, key, sources):
        for src in sources:
            if isinstance(src, dict) and key in src:
                return src[key]
        return None

    def enable_hot_reload(self, paths, callback, poll_interval=1.0):
        self._stop_event = threading.Event()
        # initialize modification times
        mtimes = {}
        for p in paths:
            try:
                mtimes[p] = os.stat(p).st_mtime
            except Exception:
                mtimes[p] = None
        def watch():
            while not self._stop_event.is_set():
                for p in paths:
                    try:
                        m = os.stat(p).st_mtime
                    except Exception:
                        m = None
                    if mtimes.get(p) is None:
                        mtimes[p] = m
                    elif m is not None and m != mtimes[p]:
                        mtimes[p] = m
                        callback(p)
                time.sleep(poll_interval)
        self._watch_thread = threading.Thread(target=watch, daemon=True)
        self._watch_thread.start()

    def stop_hot_reload(self):
        if self._stop_event:
            self._stop_event.set()
        if self._watch_thread:
            self._watch_thread.join()
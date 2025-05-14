import os
import threading
import time

try:
    import yaml
except ImportError:
    yaml = None

from .utils import load_yaml
from .merge import merge_configs

class ConfigManager:
    def __init__(self, defaults=None, dev_mode=False):
        self.config = {}
        self.defaults = defaults or {}
        self._default_factories = {}
        self.dev_mode = dev_mode
        self._watch_stop = False
        self._watch_threads = []

    def load(self, path):
        cfg = load_yaml(path)
        self.config = merge_configs(self.defaults, cfg or {})
        return self.config

    def watch_config_file(self, path, callback):
        if not self.dev_mode:
            return
        def run():
            try:
                last = os.path.getmtime(path)
            except Exception:
                last = None
            while not self._watch_stop:
                try:
                    m = os.path.getmtime(path)
                    if last is None or m != last:
                        last = m
                        callback()
                except Exception:
                    pass
                time.sleep(0.1)
        t = threading.Thread(target=run, daemon=True)
        t.start()
        self._watch_threads.append(t)

    def stop_watch(self):
        self._watch_stop = True
        for t in self._watch_threads:
            t.join(timeout=1)

    def override_cli_args(self, args):
        for k, v in vars(args).items():
            if v is not None:
                self.config[k] = v

    def set_default_factory(self, key, factory):
        self._default_factories[key] = factory

    def get(self, key, default=None):
        if key in self.config:
            return self.config[key]
        if key in self._default_factories:
            return self._default_factories[key]()
        return default

    def set(self, key, value):
        self.config[key] = value

    def serialize(self, fmt='yaml'):
        if fmt == 'yaml':
            if yaml is None:
                raise ImportError("PyYAML is required for serialize")
            return yaml.safe_dump(self.config)
        raise ValueError(f"Unsupported format: {fmt}")

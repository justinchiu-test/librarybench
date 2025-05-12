import os
import sys
import argparse
import threading
import time
from datetime import timedelta
import ipaddress

try:
    import tomllib as toml
except ImportError:
    import toml

class Config:
    def __init__(self, defaults=None, config_files=None, env_prefix='MYAPP_', coercers=None):
        self.defaults = defaults or {}
        self.config_files = config_files or []
        self.env_prefix = env_prefix
        self.coercers = coercers or {}
        self._watch_callbacks = []
        self._data = {}

    def load(self):
        data = {}
        # 1) Defaults
        data = self._nested_merge(data, self.defaults)

        # 2) TOML files
        for f in self.config_files:
            if f.endswith('.toml') and os.path.exists(f):
                # tomllib requires a binary file handle
                is_stdlib = hasattr(toml, 'loads') and toml.__name__ == 'tomllib'
                mode = 'rb' if is_stdlib else 'r'
                with open(f, mode) as fp:
                    cfg = toml.load(fp)
                data = self._nested_merge(data, cfg)

        # 3) Environment
        for k, v in os.environ.items():
            if not k.startswith(self.env_prefix):
                continue
            path = k[len(self.env_prefix):].lower().split('__')
            d = data
            for p in path[:-1]:
                if p not in d or not isinstance(d[p], dict):
                    d[p] = {}
                d = d[p]
            key = path[-1]
            full_key = '.'.join(path)
            val = v
            if full_key in self.coercers:
                val = self.coercers[full_key](v)
            d[key] = val

        # 4) CLI args
        parser = argparse.ArgumentParser()
        flat = self._flatten(data)
        dest_map = {}
        for key, val in flat.items():
            dest_name = key.replace('.', '_')
            dest_map[dest_name] = key

            arg = '--' + key.replace('.', '-')
            arg_kwargs = {'dest': dest_name}

            if key in self.coercers:
                arg_kwargs['type'] = self.coercers[key]
                arg_kwargs['default'] = None
            elif isinstance(val, bool):
                arg_kwargs['action'] = 'store_true'
                arg_kwargs['default'] = None
            else:
                arg_kwargs['type'] = type(val)
                arg_kwargs['default'] = None

            parser.add_argument(arg, **arg_kwargs)

        args, _ = parser.parse_known_args()
        for dest_name, v in vars(args).items():
            if v is not None:
                original_key = dest_map.get(dest_name, dest_name)
                parts = original_key.split('.')
                d = data
                for p in parts[:-1]:
                    if p not in d or not isinstance(d[p], dict):
                        d[p] = {}
                    d = d[p]
                d[parts[-1]] = v

        self._data = data
        return data

    def _nested_merge(self, a, b):
        if not isinstance(b, dict):
            return b
        result = dict(a)
        for k, v in b.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = self._nested_merge(result[k], v)
            else:
                result[k] = v
        return result

    def _flatten(self, d, parent_key=''):
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(self._flatten(v, new_key))
            else:
                items[new_key] = v
        return items

    def register_watch(self, callback):
        self._watch_callbacks.append(callback)

    def watch(self, interval=1):
        mtimes = {}
        files = list(self.config_files)

        def poll():
            while True:
                time.sleep(interval)
                changed = False
                for f in files:
                    if not os.path.exists(f):
                        continue
                    m = os.path.getmtime(f)
                    if f not in mtimes or mtimes[f] != m:
                        mtimes[f] = m
                        changed = True
                if changed:
                    self.load()
                    for cb in self._watch_callbacks:
                        try:
                            cb(self._data)
                        except Exception:
                            pass

        thread = threading.Thread(target=poll, daemon=True)
        thread.start()

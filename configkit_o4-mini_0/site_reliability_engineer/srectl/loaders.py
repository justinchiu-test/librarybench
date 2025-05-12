import os
import argparse

try:
    import tomllib as toml_pkg
except ImportError:
    import toml as toml_pkg

from srectl.utils import nested_merge, custom_coerce

class TOMLLoader:
    def __init__(self, path):
        self.path = path

    def load(self):
        if not self.path or not os.path.exists(self.path):
            return {}
        with open(self.path, 'rb') as f:
            data = toml_pkg.load(f)
        return data

class EnvLoader:
    def __init__(self, prefix='SRE_'):
        self.prefix = prefix

    @staticmethod
    def _flatten(d, parent_key=''):
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(EnvLoader._flatten(v, new_key))
            else:
                items[new_key] = v
        return items

    @staticmethod
    def _unflatten(flat):
        result = {}
        for key, value in flat.items():
            parts = key.split('.')
            d = result
            for p in parts[:-1]:
                d = d.setdefault(p, {})
            d[parts[-1]] = value
        return result

    def load(self, config):
        flat = self._flatten(config)
        overrides = {}
        for key in flat:
            env_key = self.prefix + key.upper().replace('.', '_')
            if env_key in os.environ:
                raw = os.environ[env_key]
                overrides[key] = custom_coerce(raw)
        if not overrides:
            return config
        unflat = self._unflatten(overrides)
        return nested_merge(config, unflat)

class ArgvLoader:
    def __init__(self, argv=None):
        self.argv = argv or []

    @staticmethod
    def _flatten(d, parent_key=''):
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(ArgvLoader._flatten(v, new_key))
            else:
                items[new_key] = v
        return items

    @staticmethod
    def _unflatten(flat):
        result = {}
        for key, value in flat.items():
            parts = key.split('.')
            d = result
            for p in parts[:-1]:
                d = d.setdefault(p, {})
            d[parts[-1]] = value
        return result

    def load(self, config):
        flat = self._flatten(config)
        parser = argparse.ArgumentParser(add_help=False)
        mapping = {}
        for key in flat:
            dest = key.replace('.', '_')
            mapping[dest] = key
            parser.add_argument(f"--{key}", dest=dest, type=str)
        args, _ = parser.parse_known_args(self.argv)
        overrides = {}
        for dest, raw in vars(args).items():
            if raw is not None:
                key = mapping[dest]
                overrides[key] = custom_coerce(raw)
        if not overrides:
            return config
        unflat = self._unflatten(overrides)
        return nested_merge(config, unflat)

import os
import tomllib

class TOMLLoader:
    @staticmethod
    def load(path):
        # Use the built-in tomllib (Python 3.11+)
        with open(path, 'rb') as f:
            return tomllib.load(f)

class EnvLoader:
    PREFIX = 'GAME_'

    @staticmethod
    def load():
        config = {}
        for k, v in os.environ.items():
            if not k.startswith(EnvLoader.PREFIX):
                continue
            raw = k[len(EnvLoader.PREFIX):].lower()
            # support double-underscore for nesting; fallback to single underscore
            if '__' in raw:
                key_path = raw.split('__')
            elif '_' in raw:
                key_path = raw.split('_')
            else:
                key_path = [raw]
            d = config
            for part in key_path[:-1]:
                d = d.setdefault(part, {})
            d[key_path[-1]] = v
        return config

class ArgvLoader:
    def __init__(self, argv=None):
        self.argv = argv or []

    def load(self):
        config = {}
        for arg in self.argv:
            if arg.startswith('--') and '=' in arg:
                key, val = arg[2:].split('=', 1)
                config[key] = val
        return config

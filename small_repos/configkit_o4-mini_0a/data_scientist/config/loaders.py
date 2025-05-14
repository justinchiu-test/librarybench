import os
import toml
import argparse

class TOMLLoader:
    @staticmethod
    def load(path):
        # Open in binary mode so tomllib.load can process it correctly
        with open(path, 'rb') as f:
            return toml.load(f)

class EnvLoader:
    @staticmethod
    def load():
        config = {}
        for k, v in os.environ.items():
            if k.startswith('DS_'):
                key = k[3:].lower()
                config[key] = v
        return config

class ArgvLoader:
    @staticmethod
    def load(schema, argv=None):
        parser = argparse.ArgumentParser()
        for key, val in schema.items():
            arg_type = type(val)
            if arg_type is bool:
                parser.add_argument(f'--{key}', action='store_true')
            else:
                parser.add_argument(f'--{key}', type=arg_type)
        args, _ = parser.parse_known_args(argv)
        return {k: v for k, v in vars(args).items() if v is not None}

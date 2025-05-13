import os
import threading
import time
import argparse
from collections import defaultdict

try:
    import yaml
except ImportError:
    yaml = None

class ConfigError(Exception):
    pass

class Config:
    def __init__(self, schema=None):
        # Different layers
        self._base = {}
        self._env_file = {}
        self._env_vars = {}
        self._cli = {}
        self._runtime = {}
        self._defaults = {}
        self._schema = schema.copy() if schema else {}
        # Plugins: loader, validator, post
        self._plugins = {'loader': [], 'validator': [], 'post': []}
        # Watcher
        self._watch_thread = None
        self._watched_file = None
        self._watched_mtime = None

    # --- Loading ---
    def load_yaml(self, filepath):
        if yaml is None:
            raise ConfigError("PyYAML is not installed")
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f) or {}
        self._base = data
        return data

    def load_dotenv(self, filepath):
        data = {}
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        k, v = line.split('=', 1)
                        data[k.strip()] = v.strip()
        except FileNotFoundError:
            return {}
        self._env_file = data
        return data

    # --- Plugins ---
    def register_plugin(self, plugin_type, func):
        if plugin_type not in self._plugins:
            raise ConfigError(f"Unknown plugin type: {plugin_type}")
        self._plugins[plugin_type].append(func)

    # --- CLI ---
    def override_cli_args(self, args):
        # args: list or Namespace
        if isinstance(args, argparse.Namespace):
            args = vars(args)
        elif isinstance(args, list):
            parser = argparse.ArgumentParser(add_help=False)
            # assume --key=value
            for a in args:
                if a.startswith('--') and '=' in a:
                    key = a.split('=', 1)[0][2:]
                    parser.add_argument(f'--{key}')
            ns, _ = parser.parse_known_args(args)
            args = {k: v for k, v in vars(ns).items() if v is not None}
        else:
            raise ConfigError("Unsupported args type")
        self._cli.update(args)
        return args

    # --- Schema ---
    def compose_schema(self, **subschemas):
        for name, schema in subschemas.items():
            if not isinstance(schema, dict):
                raise ConfigError("Schema must be dicts")
            for k, v in schema.items():
                self._schema[k] = v

    def set_default_factory(self, key, factory):
        if not callable(factory):
            raise ConfigError("Factory must be callable")
        self._defaults[key] = factory

    # --- Env Vars ---
    def load_env_vars(self, prefix=None):
        data = {}
        for k, v in os.environ.items():
            if prefix:
                if k.startswith(prefix):
                    data[k[len(prefix):]] = v
            else:
                data[k] = v
        self._env_vars = data
        return data

    # --- Merge ---
    def merge_configs(self):
        merged = {}
        # order: base < env_file < env_vars < cli < runtime
        for layer in (self._base, self._env_file, self._env_vars, self._cli, self._runtime):
            merged.update(layer)
        # apply defaults
        for k, factory in self._defaults.items():
            if k not in merged:
                merged[k] = factory()
        # run validators
        for validator in self._plugins['validator']:
            validator(merged, self._schema)
        # post processing
        for post in self._plugins['post']:
            post(merged)
        # run loader plugins (post load)
        for loader in self._plugins['loader']:
            loader(merged)
        return merged

    # --- Programmatic API ---
    def get(self, key, default=None):
        merged = self.merge_configs()
        if key in merged:
            # type check
            if key in self._schema:
                expected = self._schema[key]
                actual = merged[key]
                if not isinstance(actual, expected):
                    self.report_error(
                        f"Key '{key}' expected type {expected}, got {type(actual)}"
                    )
            return merged[key]
        return default

    def set(self, key, value):
        self._runtime[key] = value

    def to_dict(self):
        return self.merge_configs()

    # --- Error reporting ---
    def report_error(
        self, message,
        filename=None, lineno=None,
        section=None, key=None,
        expected=None, actual=None,
        suggestion=None
    ):
        parts = []
        if filename:
            parts.append(f"File '{filename}'")
        if lineno:
            parts.append(f"Line {lineno}")
        if section:
            parts.append(f"Section '{section}'")
        if key:
            parts.append(f"Key '{key}'")
        if expected is not None or actual is not None:
            parts.append(f"Expected {expected}, got {actual}")
        parts.append(message)
        if suggestion:
            parts.append(f"Suggestion: {suggestion}")
        full = "; ".join(parts)
        raise ConfigError(full)

    # --- File watch ---
    def watch_config_file(self, filepath, interval=0.5):
        if self._watch_thread:
            return
        self._watched_file = filepath
        try:
            self._watched_mtime = os.path.getmtime(filepath)
        except OSError:
            self._watched_mtime = None

        def _watch():
            while True:
                try:
                    m = os.path.getmtime(self._watched_file)
                except OSError:
                    m = None
                if m != self._watched_mtime:
                    self._watched_mtime = m
                    try:
                        self.load_yaml(self._watched_file)
                    except Exception:
                        pass
                time.sleep(interval)

        t = threading.Thread(target=_watch, daemon=True)
        t.start()
        self._watch_thread = t

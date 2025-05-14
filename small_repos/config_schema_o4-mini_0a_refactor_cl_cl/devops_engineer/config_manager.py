import json
import os
import threading
import configparser
from functools import wraps

_cache = {}
_cache_lock = threading.Lock()


class ValidationError(Exception):
    def __init__(self, file, line, section, key, expected, actual):
        self.file = file
        self.line = line
        self.section = section
        self.key = key
        self.expected = expected
        self.actual = actual
        message = f"{file}:{line} [{section}] {key}: expected {expected}, got {actual}. Suggestion: {self.suggest_fix()}"
        super().__init__(message)

    def suggest_fix(self):
        return f"Ensure '{self.key}' under section '{self.section}' is of type {self.expected}"


def expand_env_vars(config):
    import re
    pattern = re.compile(r'\$\{(\w+)\}|\$(\w+)')

    def expand_value(value):
        if not isinstance(value, str):
            return value
        def repl(match):
            var = match.group(1) or match.group(2)
            return os.environ.get(var, '')
        return pattern.sub(repl, value)

    def recurse(obj):
        if isinstance(obj, dict):
            return {k: recurse(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [recurse(v) for v in obj]
        else:
            return expand_value(obj)

    return recurse(config)


def load_config(path):
    """
    Load config from JSON, INI or YAML file with caching, env var expansion.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    mtime = os.path.getmtime(path)
    with _cache_lock:
        if path in _cache and _cache[path][0] == mtime:
            return _cache[path][1]
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path, 'r') as f:
            data = json.load(f)
    elif ext in ('.yaml', '.yml'):
        try:
            import yaml
        except ImportError:
            raise ImportError("YAML support requires PyYAML installed")
        with open(path, 'r') as f:
            data = yaml.safe_load(f) or {}
    elif ext == '.ini':
        parser = configparser.ConfigParser()
        parser.read(path)
        data = {section: dict(parser[section]) for section in parser.sections()}
    else:
        raise ValueError(f"Unsupported config format: {ext}")
    data = expand_env_vars(data)
    with _cache_lock:
        _cache[path] = (mtime, data)
    return data


class ConfigManager:
    def __init__(self, path):
        self.path = path
        self.reload()

    def reload(self):
        self.config = load_config(self.path)

    def get(self, key_path, default=None):
        parts = key_path.split('.')
        cur = self.config
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return default
        return cur

    def set(self, key_path, value):
        parts = key_path.split('.')
        cur = self.config
        for p in parts[:-1]:
            if p not in cur or not isinstance(cur[p], dict):
                cur[p] = {}
            cur = cur[p]
        cur[parts[-1]] = value

    def export_json_schema(self):
        def map_type(val):
            if isinstance(val, bool):
                return {"type": "boolean"}
            elif isinstance(val, int):
                return {"type": "integer"}
            elif isinstance(val, float):
                return {"type": "number"}
            elif isinstance(val, str):
                return {"type": "string"}
            elif isinstance(val, list):
                items_schema = map_type(val[0]) if val else {}
                return {"type": "array", "items": items_schema}
            elif isinstance(val, dict):
                return {
                    "type": "object",
                    "properties": {k: map_type(v) for k, v in val.items()}
                }
            else:
                return {}
        return {"type": "object", "properties": {k: map_type(v) for k, v in self.config.items()}}

    def validate_types(self, schema):
        try:
            import jsonschema
        except ImportError:
            raise ImportError("Type validation requires jsonschema installed")
        try:
            jsonschema.validate(self.config, schema)
        except jsonschema.ValidationError as e:
            path = ".".join([str(p) for p in list(e.absolute_path)]) or ""
            section = path.rsplit(".", 1)[0] if "." in path else ""
            key = path.rsplit(".", 1)[-1] if path else ""
            raise ValidationError(self.path, getattr(e, 'lineno', None), section, key, e.schema, type(e.instance).__name__)

    def prompt_missing(self):
        def recurse(obj, prefix=''):
            for k, v in obj.items():
                full = f"{prefix}{k}"
                if v is None or v == '':
                    val = input(f"Enter value for {full}: ")
                    obj[k] = val
                elif isinstance(v, dict):
                    recurse(v, full + '.')
        recurse(self.config)

    def __repr__(self):
        return f"<ConfigManager path={self.path}>"


def with_config(path):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cfg = ConfigManager(path)
            return func(cfg, *args, **kwargs)
        return wrapper
    return decorator

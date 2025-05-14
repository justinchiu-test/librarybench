import os
import json
import configparser
import re
import copy
from threading import Lock

# Optional YAML support
try:
    import yaml
except ImportError:
    yaml = None

_cache = {}
_cache_lock = Lock()

class ValidationError(Exception):
    def __init__(self, filename, line, section, key, expected, actual):
        message = (
            f"Validation error in {filename}"
            + (f" at line {line}" if line else "")
            + (f", section '{section}'" if section else "")
            + (f", key '{key}': expected {expected}, got {actual}")
        )
        super().__init__(message)
        self.filename = filename
        self.line = line
        self.section = section
        self.key = key
        self.expected = expected
        self.actual = actual

def expand_env_vars(obj):
    pattern = re.compile(r'\$\{(\w+)\}|\$(\w+)')
    if isinstance(obj, str):
        def repl(m):
            var = m.group(1) or m.group(2)
            return os.environ.get(var, '')
        return pattern.sub(repl, obj)
    elif isinstance(obj, dict):
        return {k: expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [expand_env_vars(v) for v in obj]
    else:
        return obj

def load_config(path):
    path = os.path.abspath(path)
    mtime = os.path.getmtime(path)
    with _cache_lock:
        if path in _cache and _cache[path]['mtime'] == mtime:
            return copy.deepcopy(_cache[path]['config'])
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path, 'r') as f:
            cfg = json.load(f)
    elif ext in ('.yaml', '.yml'):
        if yaml is None:
            raise RuntimeError("YAML support not available")
        with open(path, 'r') as f:
            cfg = yaml.safe_load(f)
    elif ext == '.ini':
        parser = configparser.ConfigParser()
        parser.read(path)
        cfg = {s: dict(parser.items(s)) for s in parser.sections()}
    else:
        raise RuntimeError("Unsupported config format")
    cfg = expand_env_vars(cfg)
    with _cache_lock:
        _cache[path] = {'mtime': mtime, 'config': copy.deepcopy(cfg)}
    return cfg

def validate_types(config, schema, filename=None):
    for key, expected in schema.items():
        if key not in config:
            continue
        val = config[key]
        if expected is None:
            continue
        if not isinstance(val, expected):
            raise ValidationError(
                filename or "<config>",
                None,
                None,
                key,
                expected.__name__ if hasattr(expected, '__name__') else str(expected),
                type(val).__name__
            )
    return True

def export_json_schema(config):
    def schema_of(obj):
        if isinstance(obj, dict):
            return {
                "type": "object",
                "properties": {k: schema_of(v) for k, v in obj.items()},
                "required": list(obj.keys())
            }
        elif isinstance(obj, list):
            items = obj[0] if obj else {}
            return {"type": "array", "items": schema_of(items)}
        elif isinstance(obj, bool):
            return {"type": "boolean"}
        elif isinstance(obj, int):
            return {"type": "integer"}
        elif isinstance(obj, float):
            return {"type": "number"}
        else:
            return {"type": "string"}
    return {"$schema": "http://json-schema.org/draft-07/schema#", **schema_of(config)}

def prompt_missing(keys):
    for key in keys:
        if ConfigManager.get(key) is None:
            val = input(f"Enter value for '{key}': ")
            ConfigManager.set(key, val)

def with_config(*sections):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for sec in sections:
                if sec not in kwargs:
                    kwargs[sec] = ConfigManager.get(sec)
            return func(*args, **kwargs)
        return wrapper
    return decorator

class ConfigManager:
    _config = {}
    _path = None
    _mtime = None
    _lock = Lock()

    @classmethod
    def load(cls, path):
        cfg = load_config(path)
        with cls._lock:
            cls._config = cfg
            cls._path = os.path.abspath(path)
            cls._mtime = os.path.getmtime(path)
        return cfg

    @classmethod
    def get(cls, key=None):
        with cls._lock:
            if key is None:
                return copy.deepcopy(cls._config)
            return copy.deepcopy(cls._config.get(key))

    @classmethod
    def set(cls, key, value):
        with cls._lock:
            cls._config[key] = value

    @classmethod
    def serialize(cls):
        with cls._lock:
            return copy.deepcopy(cls._config)

import os
import json
import time
import threading
import configparser
import ipaddress
import re
import builtins

try:
    import yaml
except ImportError:
    yaml = None

# Make 'yaml' available in builtins so pytest.skipif(yaml is None, ...) works
builtins.yaml = yaml

_cache = {}
_cache_lock = threading.Lock()


class ValidationError(Exception):
    def __init__(self, filename, line, section, key, expected, actual, suggestion=None):
        self.filename = filename
        self.line = line
        self.section = section
        self.key = key
        self.expected = expected
        self.actual = actual
        self.suggestion = suggestion

    def __str__(self):
        parts = [
            f"File: {self.filename}",
            f"Line: {self.line}" if self.line is not None else "Line: N/A",
            f"Section: {self.section}" if self.section else "Section: N/A",
            f"Key: {self.key}",
            f"Expected: {self.expected}",
            f"Actual: {self.actual}",
        ]
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        return " | ".join(parts)


def load_yaml(path):
    if yaml is None:
        raise ImportError("PyYAML is required for YAML support")
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def load_config(path):
    st = os.stat(path)
    key = (path, st.st_mtime)
    with _cache_lock:
        if key in _cache:
            return _cache[key]
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path, 'r') as f:
            data = json.load(f)
    elif ext in ('.ini',):
        parser = configparser.ConfigParser()
        parser.read(path)
        data = {}
        for section in parser.sections():
            data[section] = {}
            for k, v in parser.items(section):
                data[section][k] = v
    elif ext in ('.yaml', '.yml'):
        data = load_yaml(path)
    else:
        raise ValueError(f"Unsupported config format: {ext}")
    cm = ConfigManager(data, path)
    with _cache_lock:
        _cache[key] = cm
    return cm


def with_config(func):
    def wrapper(config_path, *args, **kwargs):
        cfg = load_config(config_path)
        return func(cfg, *args, **kwargs)
    return wrapper


class ConfigManager:
    def __init__(self, data, filename=None):
        self._data = data or {}
        self.filename = filename

    def get(self, key_path, default=None):
        parts = key_path.split('.')
        d = self._data
        for p in parts:
            if isinstance(d, dict) and p in d:
                d = d[p]
            else:
                return default
        return d

    def set(self, key_path, value):
        parts = key_path.split('.')
        d = self._data
        for p in parts[:-1]:
            if p not in d or not isinstance(d[p], dict):
                d[p] = {}
            d = d[p]
        d[parts[-1]] = value

    def to_dict(self):
        return json.loads(json.dumps(self._data))

    def expand_env_vars(self):
        pattern = re.compile(r'\$\{?(\w+)\}?')
        def _recurse(obj):
            if isinstance(obj, dict):
                return {k: _recurse(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_recurse(v) for v in obj]
            elif isinstance(obj, str):
                def repl(m):
                    return os.environ.get(m.group(1), m.group(0))
                return pattern.sub(repl, obj)
            else:
                return obj
        self._data = _recurse(self._data)

    def validate_types(self, types_map):
        for key_path, expected in types_map.items():
            val = self.get(key_path)
            if expected == 'ip':
                try:
                    ipaddress.ip_address(val)
                except Exception:
                    raise ValidationError(self.filename, None, None, key_path, 'IP address', val,
                                          suggestion="Use a valid IP string")
            elif expected == 'port':
                if not isinstance(val, int) or not (1 <= val <= 65535):
                    raise ValidationError(self.filename, None, None, key_path, 'port 1-65535', val)
            elif expected == 'bool':
                if not isinstance(val, bool):
                    raise ValidationError(self.filename, None, None, key_path, 'boolean', val)
            elif expected == 'token':
                if not isinstance(val, str) or not val:
                    raise ValidationError(self.filename, None, None, key_path, 'non-empty string', val)
            else:
                if expected == 'string':
                    if not isinstance(val, str):
                        raise ValidationError(self.filename, None, None, key_path, 'string', val)
                elif expected == 'integer':
                    if not isinstance(val, int):
                        raise ValidationError(self.filename, None, None, key_path, 'integer', val)

    def export_json_schema(self):
        def infer(v):
            if isinstance(v, bool):
                return {"type": "boolean"}
            if isinstance(v, int):
                return {"type": "integer"}
            if isinstance(v, str):
                return {"type": "string"}
            if isinstance(v, list):
                if v:
                    return {"type": "array", "items": infer(v[0])}
                else:
                    return {"type": "array"}
            if isinstance(v, dict):
                return {"type": "object", "properties": {k: infer(vv) for k, vv in v.items()}}
            return {}
        schema = {"type": "object", "properties": {}}
        for k, v in self._data.items():
            schema["properties"][k] = infer(v)
        return schema

    def prompt_missing(self, required_keys):
        for key in required_keys:
            if self.get(key) is None:
                val = input(f"Enter value for {key}: ")
                self.set(key, val)

    def save(self, path=None):
        p = path or self.filename
        if not p:
            raise ValueError("No path specified for save")
        ext = os.path.splitext(p)[1].lower()
        if ext == '.json' or not ext:
            with open(p, 'w') as f:
                json.dump(self._data, f, indent=2)
        else:
            with open(p, 'w') as f:
                json.dump(self._data, f, indent=2)


# Expose export_json_schema at module level for tests
export_json_schema = ConfigManager.export_json_schema

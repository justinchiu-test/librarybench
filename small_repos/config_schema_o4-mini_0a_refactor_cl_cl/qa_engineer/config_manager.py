import json
import os
import threading
import configparser
import re

try:
    import yaml

    def load_yaml(path):
        """Load YAML file using PyYAML."""
        with open(path, 'r') as f:
            return yaml.safe_load(f)
except ImportError:
    yaml = None

    def load_yaml(path):
        """
        Fallback minimal YAML loader for simple mappings and scalars.
        Supports nested dicts via indentation and simple int/float/string conversion.
        """
        data = {}
        stack = [(-1, data)]
        with open(path, 'r') as f:
            for raw in f:
                line = raw.rstrip('\n')
                # skip empty or comment lines
                if not line.strip() or line.lstrip().startswith('#'):
                    continue
                indent = len(line) - len(line.lstrip(' '))
                content = line.lstrip(' ')
                if ':' not in content:
                    continue
                key, val = content.split(':', 1)
                key = key.strip()
                val = val.strip()
                # find correct parent based on indent
                while stack and indent <= stack[-1][0]:
                    stack.pop()
                parent = stack[-1][1]
                if val == '':
                    # nested mapping
                    parent[key] = {}
                    stack.append((indent, parent[key]))
                else:
                    # scalar value
                    # try integer
                    if re.fullmatch(r'[+-]?\d+', val):
                        v = int(val)
                    else:
                        # try float
                        try:
                            v = float(val)
                        except ValueError:
                            v = val
                    parent[key] = v
        return data

# Simple JSON schema validator import (unused here but kept for completeness)
try:
    import jsonschema
except ImportError:
    jsonschema = None

_cache = {}
_cache_lock = threading.Lock()

class ValidationError(Exception):
    def __init__(self, file, key, expected, actual, message=None, line=None, section=None):
        self.file = file
        self.key = key
        self.expected = expected
        self.actual = actual
        self.line = line
        self.section = section
        msg = message or f"Validation error in {file}: key '{key}' expected {expected}, got {actual}"
        super().__init__(msg)

def load_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def load_ini(path):
    parser = configparser.ConfigParser()
    parser.read(path)
    data = {}
    for section in parser.sections():
        data[section] = {}
        for k, v in parser.items(section):
            data[section][k] = v
    return data

def expand_env_vars(obj):
    pattern = re.compile(r'\$\{([^}]+)\}')
    if isinstance(obj, dict):
        return {k: expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [expand_env_vars(v) for v in obj]
    elif isinstance(obj, str):
        def repl(m):
            return os.environ.get(m.group(1), "")
        return pattern.sub(repl, obj)
    else:
        return obj

def load_config(path):
    with _cache_lock:
        if path in _cache:
            return _cache[path]
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        data = load_json(path)
    elif ext == '.ini':
        data = load_ini(path)
    elif ext in ('.yaml', '.yml'):
        data = load_yaml(path)
    else:
        raise ValueError(f"Unsupported extension '{ext}'")
    data = expand_env_vars(data)
    with _cache_lock:
        _cache[path] = data
    return data

def infer_schema(obj):
    if isinstance(obj, dict):
        props = {}
        req = []
        for k, v in obj.items():
            props[k] = infer_schema(v)
            req.append(k)
        return {"type": "object", "properties": props, "required": req}
    elif isinstance(obj, list):
        if obj:
            item_schema = infer_schema(obj[0])
        else:
            item_schema = {}
        return {"type": "array", "items": item_schema}
    else:
        t = type(obj)
        if t is str:
            jtype = "string"
        elif t is bool:
            jtype = "boolean"
        elif t is int:
            jtype = "integer"
        elif t is float:
            jtype = "number"
        elif obj is None:
            jtype = "null"
        else:
            jtype = "string"
        return {"type": jtype}

def export_json_schema(path):
    cfg = load_config(path)
    schema = infer_schema(cfg)
    schema.setdefault("type", "object")
    return {"$schema": "http://json-schema.org/draft-07/schema#", **schema}

class ConfigManager:
    def __init__(self, path, prompt=True):
        self._path = path
        self._config = load_config(path)
        self._prompt = prompt

    def get(self, key_path, default=None, prompt_missing=False):
        parts = key_path.split('.')
        cur = self._config
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                if prompt_missing and self._prompt and not os.environ.get('CI'):
                    val = input(f"Enter value for {key_path}: ")
                    self.set(key_path, val)
                    return val
                if default is not None:
                    return default
                raise KeyError(f"Missing config key '{key_path}'")
        return cur

    def set(self, key_path, value):
        parts = key_path.split('.')
        cur = self._config
        for p in parts[:-1]:
            if p not in cur or not isinstance(cur[p], dict):
                cur[p] = {}
            cur = cur[p]
        cur[parts[-1]] = value

    def validate_types(self):
        # Load fresh/original config (bypassing cache) to infer schema
        ext = os.path.splitext(self._path)[1].lower()
        if ext == '.json':
            orig = load_json(self._path)
        elif ext == '.ini':
            orig = load_ini(self._path)
        elif ext in ('.yaml', '.yml'):
            orig = load_yaml(self._path)
        else:
            raise ValueError(f"Unsupported extension '{ext}'")
        orig = expand_env_vars(orig)
        schema = infer_schema(orig)
        schema.setdefault("type", "object")

        def _check(inst, sch, path):
            expected = sch.get("type")
            # OBJECT
            if expected == "object":
                if not isinstance(inst, dict):
                    actual = type(inst).__name__
                    raise ValidationError(self._path, path, expected, actual)
                props = sch.get("properties", {})
                for key, subsch in props.items():
                    if key in inst:
                        subpath = key if not path else f"{path}.{key}"
                        _check(inst[key], subsch, subpath)
            # ARRAY
            elif expected == "array":
                if not isinstance(inst, list):
                    actual = type(inst).__name__
                    raise ValidationError(self._path, path, expected, actual)
                items_sch = sch.get("items", {})
                for item in inst:
                    _check(item, items_sch, path)
            # STRING
            elif expected == "string":
                if not isinstance(inst, str):
                    actual = type(inst).__name__
                    raise ValidationError(self._path, path, expected, actual)
            # INTEGER
            elif expected == "integer":
                if not (isinstance(inst, int) and not isinstance(inst, bool)):
                    actual = type(inst).__name__
                    raise ValidationError(self._path, path, expected, actual)
            # NUMBER
            elif expected == "number":
                if not ((isinstance(inst, (int, float)) and not isinstance(inst, bool))):
                    actual = type(inst).__name__
                    raise ValidationError(self._path, path, expected, actual)
            # BOOLEAN
            elif expected == "boolean":
                if not isinstance(inst, bool):
                    actual = type(inst).__name__
                    raise ValidationError(self._path, path, expected, actual)
            # NULL
            elif expected == "null":
                if inst is not None:
                    actual = type(inst).__name__
                    raise ValidationError(self._path, path, expected, actual)
            # other types are not strictly enforced

        # Run the check against current (possibly modified) config
        _check(self._config, schema, "")
        # If no mismatches, succeed silently

    def export_json_schema(self):
        return export_json_schema(self._path)

def with_config(path):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            cm = ConfigManager(path)
            kwargs['config'] = cm
            return fn(*args, **kwargs)
        return wrapper
    return decorator

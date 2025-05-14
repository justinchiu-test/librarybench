import os
import json
import configparser
import inspect
import functools
import textwrap

try:
    import yaml
except ImportError:
    yaml = None

try:
    import numpy as _np
except ImportError:
    _np = None

_cache = {}

class ValidationError(Exception):
    def __init__(self, file=None, line=None, section=None, key=None, message="", suggestions=None):
        self.file = file
        self.line = line
        self.section = section
        self.key = key
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(self.__str__())

    def __str__(self):
        parts = []
        if self.file:
            parts.append(f"File '{self.file}'")
        if self.line:
            parts.append(f"Line {self.line}")
        if self.section:
            parts.append(f"In section '{self.section}'")
        if self.key:
            parts.append(f"Key '{self.key}'")
        loc = ": ".join(parts) if parts else ""
        msg = self.message or ""
        sug = ""
        if self.suggestions:
            sug = " Suggestions: " + ", ".join(self.suggestions)
        return f"{loc}: {msg}.{sug}"

def load_yaml(path):
    """
    Load a YAML file. If PyYAML is available, use it; otherwise, use a minimal fallback parser.
    """
    with open(path, 'r') as f:
        content = f.read()
    content = textwrap.dedent(content)

    # Always use yaml.safe_load (we provide a fallback if PyYAML is missing)
    return yaml.safe_load(content)

def expand_env_vars(obj):
    if isinstance(obj, str):
        return os.path.expandvars(obj)
    if isinstance(obj, list):
        return [expand_env_vars(v) for v in obj]
    if isinstance(obj, dict):
        return {k: expand_env_vars(v) for k, v in obj.items()}
    return obj

def _infer_type(value):
    """
    Convert a string from an INI or YAML scalar into bool/int/float/list/str by value.
    If it's comma‐separated, split and recursively infer each element.
    """
    if isinstance(value, str):
        v = value.strip()
        # boolean?
        low = v.lower()
        if low == 'true':
            return True
        if low == 'false':
            return False
        # integer?
        if v.isdigit() or (v.startswith('-') and v[1:].isdigit()):
            return int(v)
        # float?
        try:
            fv = float(v)
            return fv
        except ValueError:
            pass
        # comma-list?
        if ',' in v:
            items = [item.strip() for item in v.split(',')]
            return [_infer_type(item) for item in items]
        # fallback to string
        return v
    return value

# If PyYAML isn't installed, provide a dummy yaml.safe_load that uses our minimal parser:
if yaml is None:
    def _yaml_safe_load(content):
        content = textwrap.dedent(content)
        lines = content.splitlines()

        def _parse_block(lines, start, indent):
            result = None
            i = start
            while i < len(lines):
                line = lines[i]
                # skip blank lines
                if not line.strip():
                    i += 1
                    continue
                curr_indent = len(line) - len(line.lstrip(' '))
                if curr_indent < indent:
                    break
                content_line = line.lstrip(' ')
                # list item
                if content_line.startswith('- '):
                    if result is None:
                        result = []
                    elif not isinstance(result, list):
                        raise ValidationError(line=i+1,
                                              message="Mixed types in YAML list")
                    val_str = content_line[2:]
                    if val_str.strip() == '':
                        val, consumed = _parse_block(lines, i+1, curr_indent+2)
                        result.append(val)
                        i = i + 1 + consumed
                    else:
                        result.append(_infer_type(val_str))
                        i += 1
                # mapping entry
                elif ':' in content_line:
                    if result is None:
                        result = {}
                    elif not isinstance(result, dict):
                        raise ValidationError(line=i+1,
                                              message="Mixed types in YAML mapping")
                    key, rest = content_line.split(':', 1)
                    key = key.strip()
                    rest = rest.strip()
                    if rest != '':
                        result[key] = _infer_type(rest)
                        i += 1
                    else:
                        val, consumed = _parse_block(lines, i+1, curr_indent+2)
                        result[key] = val
                        i = i + 1 + consumed
                else:
                    # scalar line
                    scalar = _infer_type(content_line)
                    result = scalar
                    i += 1
            consumed = i - start
            return result, consumed

        parsed, _ = _parse_block(lines, 0, 0)
        return parsed

    class _DummyYAML:
        safe_load = staticmethod(_yaml_safe_load)
    yaml = _DummyYAML

def validate_types(name, value, expected_type):
    if expected_type is inspect._empty:
        return
    if expected_type is None:
        return
    # numpy array support
    if _np is not None and expected_type is _np.ndarray:
        if not isinstance(value, _np.ndarray):
            raise ValidationError(
                key=name,
                message=f"Expected numpy.ndarray for '{name}'",
                suggestions=[str(expected_type)]
            )
        return
    # basic type check
    if not isinstance(value, expected_type):
        raise ValidationError(
            key=name,
            message=f"Type mismatch for '{name}': expected {expected_type.__name__}, got {type(value).__name__}",
            suggestions=[expected_type.__name__]
        )

def prompt_missing(key, expected_type):
    while True:
        inp = input(f"Enter value for {key} ({expected_type.__name__}): ")
        if not inp:
            continue
        try:
            if expected_type is int:
                return int(inp)
            if expected_type is float:
                return float(inp)
            if expected_type is list:
                # simple comma split, leave as strings
                return [x.strip() for x in inp.split(',')]
            if _np is not None and expected_type is _np.ndarray:
                import numpy as np
                parts = inp.split(',')
                return np.array([float(x) for x in parts])
            return inp
        except Exception as e:
            print(f"Invalid input: {e}")

class ConfigManager:
    def __init__(self, data, file_path=None):
        self._data = data or {}
        self._file = file_path

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        existing = self._data.get(key)
        if existing is not None:
            if not isinstance(value, type(existing)):
                raise ValidationError(
                    file=self._file,
                    key=key,
                    message=f"Type mismatch on set: '{key}' expected {type(existing).__name__}",
                    suggestions=[type(existing).__name__]
                )
        self._data[key] = value

    def export_json_schema(self):
        def _type_map(v):
            if isinstance(v, bool):
                return "boolean"
            if isinstance(v, int) and not isinstance(v, bool):
                return "integer"
            if isinstance(v, float):
                return "number"
            if isinstance(v, str):
                return "string"
            if isinstance(v, list):
                return "array"
            if isinstance(v, dict):
                return "object"
            if _np is not None and isinstance(v, _np.ndarray):
                return "array"
            return "string"

        props = {}
        for k, v in self._data.items():
            props[k] = {"type": _type_map(v), "default": v}
        schema = {"type": "object", "properties": props}
        return json.dumps(schema, indent=2)

def load_config(path):
    if path in _cache:
        return _cache[path]
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == '.json':
            with open(path, 'r') as f:
                data = json.load(f)
        elif ext in ('.yaml', '.yml'):
            data = load_yaml(path)
        elif ext == '.ini':
            cp = configparser.ConfigParser()
            cp.read(path)
            sec = cp['DEFAULT']
            data = {}
            for k, v in sec.items():
                data[k] = _infer_type(v)
        else:
            raise ValidationError(file=path, message=f"Unsupported file extension '{ext}'")
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(file=path, message=str(e))

    data = expand_env_vars(data)
    cfg = ConfigManager(data, path)
    _cache[path] = cfg
    return cfg

def with_config(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cfg = load_config(path)
            sig = inspect.signature(func)
            bound = {}

            for name, param in sig.parameters.items():
                if name in kwargs:
                    val = kwargs[name]
                elif cfg.get(name) is not None:
                    val = cfg.get(name)
                elif param.default is not inspect._empty:
                    val = param.default
                else:
                    exp_type = param.annotation if param.annotation is not inspect._empty else str
                    val = prompt_missing(name, exp_type)

                exp_type = param.annotation if param.annotation is not inspect._empty else None
                if exp_type:
                    validate_types(name, val, exp_type)

                bound[name] = val
                cfg._data[name] = val

            return func(**bound)
        return wrapper
    return decorator

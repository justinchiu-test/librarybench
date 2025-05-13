import os
import json
import threading
import difflib
import re

try:
    import yaml
except ImportError:
    yaml = None

def ensure_thread_safety(method):
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    wrapper.__wrapped__ = method
    return wrapper

class ConfigManager:
    def __init__(self, defaults=None, schema=None):
        self._lock = threading.RLock()
        self._config = {}
        if defaults:
            self._config = self.merge_configs(defaults)
        self._schema = schema or {}
        self._validators = {}      # path -> [funcs]
        self._on_load_hooks = {}   # path -> [funcs]
        self._on_access_hooks = {} # path -> [funcs]

    @ensure_thread_safety
    def load_file(self, path):
        # load JSON or YAML (with simple fallback if PyYAML not present)
        if path.endswith(('.yaml', '.yml')):
            if yaml:
                with open(path) as f:
                    data = yaml.safe_load(f) or {}
            else:
                data = {}
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if ':' in line:
                            k, v = line.split(':', 1)
                            data[k.strip()] = v.strip()
        else:
            with open(path) as f:
                data = json.load(f)
        # merge, interpolate, validate
        self._config = self.merge_configs(self._config, data)
        self.interpolate()
        self.validate_schema()
        # call on_load hooks without triggering on_access
        for pth, hooks in self._on_load_hooks.items():
            for hook in hooks:
                try:
                    val = self._get_no_hooks(pth)
                except KeyError:
                    val = None
                hook(val)
        return self._config

    @ensure_thread_safety
    def merge_configs(self, *configs):
        def merge(a, b):
            result = dict(a)
            for k, v in b.items():
                if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                    result[k] = merge(result[k], v)
                else:
                    result[k] = v
            return result
        merged = {}
        for cfg in configs:
            merged = merge(merged, cfg or {})
        return merged

    @ensure_thread_safety
    def interpolate(self):
        pattern = re.compile(r'\$\{([^}]+)\}')
        def _interp(obj):
            if isinstance(obj, dict):
                return {k: _interp(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_interp(v) for v in obj]
            if isinstance(obj, str):
                def repl(m):
                    key = m.group(1)
                    if ':' in key:
                        typ, name = key.split(':', 1)
                        if typ == 'ENV':
                            return os.environ.get(name, '')
                    # fallback to env or config
                    return os.environ.get(key, str(self.get(key, '')))
                return pattern.sub(repl, obj)
            return obj
        self._config = _interp(self._config)
        return self._config

    @staticmethod
    def diff(a, b):
        if isinstance(a, ConfigManager):
            a = a._config
        if isinstance(b, ConfigManager):
            b = b._config
        a_str = json.dumps(a, indent=2, sort_keys=True).splitlines(keepends=True)
        b_str = json.dumps(b, indent=2, sort_keys=True).splitlines(keepends=True)
        diff_lines = difflib.unified_diff(a_str, b_str, fromfile='a', tofile='b')
        return ''.join(diff_lines)

    def on_load(self, path, func):
        self._on_load_hooks.setdefault(path, []).append(func)

    def on_access(self, path, func):
        self._on_access_hooks.setdefault(path, []).append(func)

    def _get_no_hooks(self, path, default=None):
        """Internal get that does not invoke on_access hooks."""
        parts = path.split('.') if path else []
        cur = self._config
        for p in parts:
            if not isinstance(cur, dict) or p not in cur:
                if default is not None:
                    return default
                raise KeyError(f"{path} not found")
            cur = cur[p]
        return cur

    @ensure_thread_safety
    def validate_schema(self):
        errors = []
        for path, spec in self._schema.items():
            try:
                val = self.get(path)
            except KeyError:
                val = None
            if spec.get('required') and val is None:
                errors.append(f"{path} is required")
                continue
            if val is not None:
                typ = spec.get('type')
                if typ and not isinstance(val, typ):
                    errors.append(f"{path} expected {typ.__name__}, got {type(val).__name__}")
                mn = spec.get('min')
                mx = spec.get('max')
                if isinstance(val, (int, float)):
                    if mn is not None and val < mn:
                        errors.append(f"{path} < min {mn}")
                    if mx is not None and val > mx:
                        errors.append(f"{path} > max {mx}")
            # custom validators
            for func in self._validators.get(path, []):
                try:
                    func(val)
                except Exception as e:
                    errors.append(f"{path} validator error: {e}")
        if errors:
            raise ValueError("Schema validation errors: " + "; ".join(errors))

    def register_validator(self, path, func):
        self._validators.setdefault(path, []).append(func)

    @ensure_thread_safety
    def get(self, path, default=None):
        parts = path.split('.') if path else []
        cur = self._config
        for p in parts:
            if not isinstance(cur, dict) or p not in cur:
                if default is not None:
                    value = default
                    break
                raise KeyError(f"{path} not found")
            cur = cur[p]
        else:
            value = cur
        for hook in self._on_access_hooks.get(path, []):
            hook(value)
        return value

    def get_int(self, path):
        v = self.get(path)
        if isinstance(v, bool):
            raise ValueError(f"{path} is bool, not int")
        try:
            return int(v)
        except:
            raise ValueError(f"{path} cannot be cast to int")

    def get_str(self, path):
        v = self.get(path)
        if v is None:
            return None
        if not isinstance(v, str):
            v = str(v)
        return v

    def get_bool(self, path):
        v = self.get(path)
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            if v.lower() in ('true', '1', 'yes'):
                return True
            if v.lower() in ('false', '0', 'no'):
                return False
        raise ValueError(f"{path} cannot be cast to bool")

    def section(self, path):
        v = self.get(path)
        if not isinstance(v, dict):
            raise ValueError(f"{path} is not a section")
        return v

    @ensure_thread_safety
    def generate_docs(self, fmt='markdown'):
        lines = []
        if fmt == 'markdown':
            lines.append("## Configuration Documentation\n")
            lines.append("| Field | Type | Required | Description | Example |\n")
            lines.append("|---|---|---|---|---|\n")
            for path, spec in self._schema.items():
                t = spec.get('type').__name__ if spec.get('type') else ''
                req = 'yes' if spec.get('required') else 'no'
                desc = spec.get('description', '')
                ex = spec.get('example', '')
                lines.append(f"| {path} | {t} | {req} | {desc} | {ex} |\n")
        else:
            lines.append("<h2>Configuration Documentation</h2>\n")
            for path, spec in self._schema.items():
                lines.append(f"<h3>{path}</h3>\n")
                lines.append(f"<p>Type: {spec.get('type').__name__ if spec.get('type') else ''}</p>\n")
                lines.append(f"<p>Required: {spec.get('required')}</p>\n")
                if spec.get('description'):
                    lines.append(f"<p>{spec.get('description')}</p>\n")
                if spec.get('example'):
                    lines.append(f"<pre>{spec.get('example')}</pre>\n")
        return ''.join(lines)

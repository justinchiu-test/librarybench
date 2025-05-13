import os
import threading
import re
import json
import difflib
from copy import deepcopy

try:
    import jsonschema
except ImportError:
    jsonschema = None

def ensure_thread_safety(method):
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapper

class Vault:
    def __init__(self, store=None):
        self._store = store or {}
    def get(self, key):
        return self._store.get(key)

class ConfigManager:
    def __init__(self, configs=None, vault=None):
        self._lock = threading.RLock()
        self._vault = vault or Vault()
        self._config = configs or {}
        self._load_hooks = {}
        self._access_hooks = {}
        self._validators = []

    @ensure_thread_safety
    def merge_configs(self, *configs):
        def deep_merge(a, b):
            result = deepcopy(a)
            for k, v in b.items():
                if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                    result[k] = deep_merge(result[k], v)
                else:
                    result[k] = deepcopy(v)
            return result
        merged = {}
        for cfg in configs:
            merged = deep_merge(merged, cfg)
        self._config = merged
        self._run_load_hooks()
        return self._config

    def register_validator(self, func):
        self._validators.append(func)

    @ensure_thread_safety
    def validate_schema(self, schema):
        # If jsonschema is available, perform schema validation
        if jsonschema is not None:
            jsonschema.validate(self._config, schema)
        # Always run custom validators
        for v in self._validators:
            v(self._config)

    @ensure_thread_safety
    def interpolate(self, value):
        if isinstance(value, str):
            pattern = re.compile(r'\$\{(.*?):(.*?)\}')
            def repl(m):
                src, key = m.group(1), m.group(2)
                if src == 'ENV':
                    return os.getenv(key, '')
                elif src == 'VAULT':
                    return str(self._vault.get(key) or '')
                else:
                    return m.group(0)
            return pattern.sub(repl, value)
        elif isinstance(value, dict):
            return {k: self.interpolate(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.interpolate(v) for v in value]
        else:
            return value

    @ensure_thread_safety
    def diff(self, other_config):
        a = json.dumps(self._config, indent=2, sort_keys=True).splitlines()
        b = json.dumps(other_config, indent=2, sort_keys=True).splitlines()
        return '\n'.join(difflib.unified_diff(a, b, fromfile='current', tofile='other', lineterm=''))

    def on_load(self, section, func):
        self._load_hooks.setdefault(section, []).append(func)

    def on_access(self, section, func):
        self._access_hooks.setdefault(section, []).append(func)

    def _run_load_hooks(self):
        for section, funcs in self._load_hooks.items():
            cfg = self.section(section, invoke_hooks=False)
            for f in funcs:
                f(cfg)

    def _run_access_hooks(self, section, cfg):
        for sec, funcs in self._access_hooks.items():
            if section.startswith(sec):
                for f in funcs:
                    f(cfg)

    @ensure_thread_safety
    def section(self, path, invoke_hooks=True):
        parts = path.split('.')
        cfg = self._config
        for p in parts:
            if not isinstance(cfg, dict) or p not in cfg:
                return None
            cfg = cfg[p]
        if invoke_hooks:
            self._run_access_hooks(path, cfg)
        return cfg

    @ensure_thread_safety
    def get(self, path, default=None):
        parts = path.split('.')
        cfg = self._config
        for p in parts:
            if not isinstance(cfg, dict) or p not in cfg:
                return default
            cfg = cfg[p]
        self._run_access_hooks(path, cfg)
        return cfg

    def get_int(self, path):
        val = self.get(path)
        try:
            return int(val)
        except Exception:
            raise TypeError(f"Value at {path} is not int")

    def get_str(self, path):
        val = self.get(path)
        if isinstance(val, str):
            return val
        else:
            raise TypeError(f"Value at {path} is not str")

    def get_bool(self, path):
        val = self.get(path)
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            if val.lower() in ('true', 'false'):
                return val.lower() == 'true'
        raise TypeError(f"Value at {path} is not bool")

    @ensure_thread_safety
    def generate_docs(self, markdown=True):
        lines = []
        def recurse(cfg, prefix=''):
            if isinstance(cfg, dict):
                for k, v in cfg.items():
                    path = f"{prefix}.{k}" if prefix else k
                    lines.append(f"- **{path}**: {type(v).__name__}")
                    recurse(v, path)
        recurse(self._config)
        if markdown:
            return "# Config Reference\n" + "\n".join(lines)
        else:
            return "<h1>Config Reference</h1>\n" + "\n".join(f"<p>{l}</p>" for l in lines)

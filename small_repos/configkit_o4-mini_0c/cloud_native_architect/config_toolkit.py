import os
import re
import threading
import time
import yaml
import toml

class ConfigToolkit:
    def __init__(self):
        self.data = {}
        self.coercers = {}
        self.hooks = {"pre_merge": [], "post_merge": [], "export": []}
        self.profile = "standard"

    def resolve_variables(self, config):
        pattern = re.compile(r"\$\{([^}]+)\}")
        def _resolve(obj):
            if isinstance(obj, str):
                def replace(match):
                    var = match.group(1)
                    val = None
                    # try dot-notation lookup
                    parts = var.split(".")
                    ctx = config
                    try:
                        for p in parts:
                            ctx = ctx[p]
                        val = ctx
                    except Exception:
                        # fallback to environment
                        val = os.environ.get(var, "")
                    return str(val)
                return pattern.sub(replace, obj)
            elif isinstance(obj, dict):
                return {k: _resolve(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_resolve(v) for v in obj]
            else:
                return obj
        return _resolve(config)

    def load_toml(self, path):
        with open(path, "r") as f:
            data = toml.load(f)
        return data

    def load_yaml(self, path):
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return data

    def register_coercer(self, type_name, func):
        self.coercers[type_name] = func

    def register_hook(self, phase, func):
        if phase not in self.hooks:
            raise ValueError(f"Unknown phase {phase}")
        self.hooks[phase].append(func)

    def merge_lists(self, global_list, tenant_list):
        merged = []
        seen = set()
        for item in global_list:
            name = item.get("name")
            if name not in seen:
                merged.append(item)
                seen.add(name)
        for item in tenant_list:
            name = item.get("name")
            if name not in seen:
                merged.append(item)
                seen.add(name)
        return merged

    def set_profile(self, profile):
        if profile not in ["standard", "enterprise", "compliance"]:
            raise ValueError("Invalid profile")
        self.profile = profile

    def get(self, path):
        parts = path.split(".")
        ctx = self.data
        for p in parts:
            ctx = ctx[p]
        return ctx

    def with_defaults(self, config, defaults):
        def _merge(a, b):
            result = dict(a)
            for k, v in b.items():
                if k not in result:
                    result[k] = v
                else:
                    if isinstance(result[k], dict) and isinstance(v, dict):
                        result[k] = _merge(result[k], v)
            return result
        return _merge(config, defaults)

    def watch_and_reload(self, paths, callback, interval=1):
        # stub implementation: immediately invoke callback
        callback()

# module-level instance and function wrappers
toolkit = ConfigToolkit()

resolve_variables = toolkit.resolve_variables
load_toml = toolkit.load_toml
load_yaml = toolkit.load_yaml
register_coercer = toolkit.register_coercer
register_hook = toolkit.register_hook
merge_lists = toolkit.merge_lists
set_profile = toolkit.set_profile
get = toolkit.get
with_defaults = toolkit.with_defaults
watch_and_reload = toolkit.watch_and_reload

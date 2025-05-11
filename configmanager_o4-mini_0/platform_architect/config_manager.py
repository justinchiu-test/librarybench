import os
import sys
import json
import copy
import logging
from datetime import datetime

# TOML parsing support
try:
    import tomllib
except ImportError:
    import toml as tomllib

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    logger.addHandler(handler)


class ConfigManager:
    def __init__(self, initial_config=None):
        self.config = copy.deepcopy(initial_config) if initial_config else {}
        self.schema = None
        self.overrides = {}
        self.plugins = {"loader": {}, "merge": {}, "alert": {}}
        self.snapshots = []
        self.events = []
        self.current_version = 0

    def register_plugin(self, plugin_type, name, hook):
        if plugin_type not in self.plugins:
            raise ValueError(f"Unknown plugin type: {plugin_type}")
        self.plugins[plugin_type][name] = hook
        self.log_event("plugin_registered", {"type": plugin_type, "name": name})

    def validate_config(self, schema):
        self.schema = schema

        def check(sch, cfg, path=""):
            for key, expected in sch.items():
                if key not in cfg:
                    raise ValueError(f"Missing key {path + key}")
                value = cfg[key]
                if isinstance(expected, dict):
                    if not isinstance(value, dict):
                        raise TypeError(f"Key {path+key} expected dict")
                    check(expected, value, path + key + ".")
                else:
                    if not isinstance(value, expected):
                        raise TypeError(f"Key {path+key} expected {expected}")
        check(self.schema, self.config)
        self.log_event("config_validated", {"schema": self.schema})
        return True

    def export_to_env(self, update_os_env=False):
        pairs = []

        def recurse(d, prefix=""):
            for k, v in d.items():
                key = (prefix + "_" + k).upper() if prefix else k.upper()
                if isinstance(v, dict):
                    recurse(v, key)
                else:
                    pair = f"{key}={v}"
                    pairs.append(pair)
                    if update_os_env:
                        os.environ[key] = str(v)
        recurse(self.config)
        self.log_event("export_to_env", {"count": len(pairs)})
        return pairs

    def log_event(self, event_type, metadata):
        entry = {
            "event": event_type,
            "metadata": metadata,
            "version": self.current_version,
            "timestamp": datetime.now().isoformat(),
        }
        for hook in self.plugins["alert"].values():
            try:
                hook(entry)
            except Exception:
                pass
        self.events.append(entry)
        # use default=str to handle non-serializable types (e.g., types in schema)
        try:
            logger.info(json.dumps(entry, default=str))
        except Exception:
            logger.info(str(entry))

    def get_namespace(self, namespace):
        keys = namespace.split(".") if namespace else []
        cfg = self.config
        for k in keys:
            if not isinstance(cfg, dict) or k not in cfg:
                return {}
            cfg = cfg[k]
        return copy.deepcopy(cfg)

    def snapshot(self):
        snap = {
            "version": self.current_version,
            "config": copy.deepcopy(self.config),
            "timestamp": datetime.now().isoformat(),
        }
        self.snapshots.append(snap)
        self.log_event("snapshot", {"version": snap["version"]})
        return snap

    def load_toml_source(self, file_path):
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
        self._merge_config(data, source=file_path)

    def load_json_source(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._merge_config(data, source=file_path)

    def load_env_source(self, prefix=None):
        data = {}
        for k, v in os.environ.items():
            if prefix is None or k.startswith(prefix):
                key = k if prefix is None else k[len(prefix):]
                data[key] = v
        self._merge_config(data, source="env")

    def _merge_config(self, new_data, source=""):
        old = copy.deepcopy(self.config)
        # loader plugins
        for hook in self.plugins["loader"].values():
            try:
                new_data = hook(new_data)
            except Exception:
                pass
        # deep merge
        self._deep_update(self.config, new_data)
        self.current_version += 1
        changes = self.diff_changes(old, self.config)
        self.log_event("config_loaded", {"source": source, "changes": changes})
        self.snapshot()

    def _deep_update(self, d, u):
        for k, v in u.items():
            if isinstance(v, dict) and isinstance(d.get(k), dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v

    def diff_changes(self, old, new):
        added = {}
        removed = {}
        changed = {}

        def recurse(o, n, path=""):
            o_keys = set(o.keys()) if isinstance(o, dict) else set()
            n_keys = set(n.keys()) if isinstance(n, dict) else set()
            for k in n_keys - o_keys:
                added[path + k] = n[k]
            for k in o_keys - n_keys:
                removed[path + k] = o[k]
            for k in n_keys & o_keys:
                ov = o[k]
                nv = n[k]
                if isinstance(ov, dict) and isinstance(nv, dict):
                    recurse(ov, nv, path + k + ".")
                else:
                    if ov != nv:
                        changed[path + k] = {"old": ov, "new": nv}
        recurse(old, new)
        return {"added": added, "removed": removed, "changed": changed}

    def override_config(self, key_path, value):
        parts = key_path.split(".")
        old = copy.deepcopy(self.config)
        d = self.config
        for p in parts[:-1]:
            if p not in d or not isinstance(d[p], dict):
                d[p] = {}
            d = d[p]
        d[parts[-1]] = value
        self.current_version += 1
        changes = self.diff_changes(old, self.config)
        self.log_event("override", {"key": key_path, "value": value, "changes": changes})
        self.snapshot()

    def parse_cli_args(self, args=None):
        if args is None:
            args = sys.argv[1:]
        for arg in args:
            if not arg.startswith("--"):
                continue
            raw = arg[2:]
            if "=" not in raw:
                self.log_event("cli_parse_error", {"arg": arg, "error": "Invalid argument format"})
                continue
            key_path, val = raw.split("=", 1)
            # cast
            if val.isdigit():
                val_cast = int(val)
            elif val.lower() in ("true", "false"):
                val_cast = val.lower() == "true"
            else:
                val_cast = val
            try:
                self.override_config(key_path, val_cast)
            except Exception as e:
                self.log_event("cli_parse_error", {"arg": arg, "error": str(e)})

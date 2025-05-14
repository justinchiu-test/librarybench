import threading
import time
from collections import defaultdict
from configsystem.yaml_loader import YAMLLoader
from configsystem.utils import DotNotationAccess, NestedMerge, VariableInterpolation
from configsystem.coercer import CustomCoercers

class ConfigWatcher:
    def __init__(self):
        self.watchers = defaultdict(list)

    def watch(self, path, callback):
        self.watchers[path].append(callback)

    def notify(self, path, value):
        # notify exact and prefix watchers
        for watch_path, callbacks in self.watchers.items():
            if path.startswith(watch_path):
                for cb in callbacks:
                    cb(path, value)

class ConfigVisualization:
    @staticmethod
    def graph(layers):
        # return simple dict of layer names and keys
        viz = {}
        for name, cfg in layers.items():
            viz[name] = list(ConfigVisualization._collect_keys(cfg))
        return viz

    @staticmethod
    def _collect_keys(cfg, prefix=''):
        keys = set()
        if isinstance(cfg, dict):
            for k, v in cfg.items():
                full = f"{prefix}.{k}" if prefix else k
                keys.add(full)
                keys |= ConfigVisualization._collect_keys(v, full)
        return keys

class ConflictReporting:
    def __init__(self):
        self.conflicts = []

    def report(self, key):
        self.conflicts.append(key)

    def get_conflicts(self):
        return self.conflicts

class ConfigManager:
    def __init__(self):
        self.base = {}
        self.mods = []
        self.profile = None
        self.watch = ConfigWatcher()
        self.coercers = CustomCoercers()
        self.defaults = {}
        self.conflict_report = ConflictReporting()

    def load_base(self, file_path):
        self.base = YAMLLoader.load(file_path)

    def add_mod(self, file_path):
        cfg = YAMLLoader.load(file_path)
        self.mods.append(cfg)

    def set_profile(self, profile):
        self.profile = profile

    def set_defaults(self, defaults):
        self.defaults = defaults

    def register_coercer(self, suffix, fn):
        self.coercers.register(suffix, fn)

    def get_merged(self):
        # start with base
        merged = dict(self.base)
        # apply profile first (so mods override it later)
        if self.profile and isinstance(merged.get('profiles'), dict):
            profile_cfg = merged.get('profiles', {}).get(self.profile, {})
            merged = NestedMerge.merge(merged, profile_cfg, self.conflict_report.conflicts)
        # apply mods
        for mod in self.mods:
            merged = NestedMerge.merge(merged, mod, self.conflict_report.conflicts)
        # apply defaults (defaults < merged)
        merged = NestedMerge.merge(self.defaults, merged)
        # apply coercers in place
        self.coercers.apply(merged)
        # apply variable interpolation
        merged = VariableInterpolation.interpolate(merged)
        return merged

    def get(self, path, default=None):
        cfg = self.get_merged()
        return DotNotationAccess.get(cfg, path, default)

    def set(self, path, value):
        # set on base
        DotNotationAccess.set(self.base, path, value)
        self.watch.notify(path, value)

    def watch_path(self, path, callback):
        self.watch.watch(path, callback)

    def visualize(self):
        layers = {'base': self.base}
        for idx, mod in enumerate(self.mods):
            layers[f'mod{idx}'] = mod
        return ConfigVisualization.graph(layers)

    def get_conflicts(self):
        return self.conflict_report.get_conflicts()

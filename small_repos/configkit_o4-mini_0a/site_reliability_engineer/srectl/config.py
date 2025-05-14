import os
from srectl.defaults import DefaultFallback
from srectl.loaders import TOMLLoader, EnvLoader, ArgvLoader
from srectl.utils import nested_merge, custom_coerce
from srectl.conflict import ConflictReporting
from srectl.watch import ConfigWatcher, HotReload

class ConfigManager:
    def __init__(self, toml_path=None, argv=None, env_prefix='SRE_'):
        self.toml_path = toml_path
        self.argv = argv or []
        self.env_prefix = env_prefix
        self.watch = ConfigWatcher()
        self._previous_config = {}
        # Setup hot reload on toml_path
        if toml_path:
            self.hotreload = HotReload([toml_path], self._on_file_change)
        else:
            self.hotreload = None
        self.config = self.load()

    def load(self):
        # Load defaults
        cfg = DefaultFallback().load()
        # Load TOML
        toml_cfg = TOMLLoader(self.toml_path).load()
        cfg = nested_merge(cfg, toml_cfg)
        # Env overrides
        cfg = EnvLoader(self.env_prefix).load(cfg)
        # Argv overrides
        cfg = ArgvLoader(self.argv).load(cfg)
        # Coerce
        cfg = self._coerce_all(cfg)
        # Detect conflicts
        ConflictReporting.detect(cfg)
        # Store previous
        self._previous_config = getattr(self, 'config', {})
        self.config = cfg
        return cfg

    def _coerce_all(self, cfg):
        if isinstance(cfg, dict):
            return {k: self._coerce_all(v) for k, v in cfg.items()}
        if isinstance(cfg, list):
            return [self._coerce_all(v) for v in cfg]
        return custom_coerce(cfg)

    def on(self, event, callback):
        self.watch.register(event, callback)

    def _on_file_change(self, path):
        # capture old threshold
        old = self.config.get('alert', {}).get('threshold')
        # read raw toml file contents for new threshold
        toml_data = TOMLLoader(self.toml_path).load()
        raw_thr = toml_data.get('alert', {}).get('threshold')
        # coerce raw threshold if present
        if raw_thr is not None:
            new = custom_coerce(raw_thr)
        else:
            new = None
        # reload full config (with env/argv overrides)
        self.load()
        # notify only based on raw toml change
        if old != new:
            self.watch.notify('alert.threshold_changed', old=old, new=new)

    def simulate_file_change(self, path):
        if self.hotreload:
            self.hotreload.simulate_change(path)

# coding: utf-8
"""
Platform engineer configuration service
"""
import os

class ConfigService:
    def __init__(self):
        self.global_config = {}
        self.tenant_configs = {}
        self.plugins = {}
        self._acl_cache = {}
        self._acl_count = 0
        self._reload_callback = None
        self.logger = None
        # default merge precedence: global < plugin < tenant < profile
        self._precedence = ['global', 'plugin', 'tenant', 'profile']

    def load_global_config(self, cfg):
        self.global_config = cfg.copy()

    def load_tenant_config(self, tenant, cfg):
        self.tenant_configs[tenant] = cfg.copy()

    def register_plugin(self, name, plugin):
        # plugin for merging or secrets
        self.plugins[name] = plugin

    def set_precedence(self, precedence):
        # precedence: list of sources in merge order
        self._precedence = precedence

    def merge_configs(self, tenant):
        # default precedence
        order = getattr(self, '_precedence', ['global', 'tenant', 'plugin', 'profile'])
        merged = {}
        # prepare plugin data
        plugin_data = {}
        for name, hook in self.plugins.items():
            try:
                plugin_data[name] = hook(tenant)
            except Exception:
                plugin_data[name] = {}
        # prepare profile override if any
        profile_data = getattr(self, 'profile_override', {})
        for source in order:
            if source == 'global':
                merged.update(self.global_config)
            elif source == 'tenant':
                merged.update(self.tenant_configs.get(tenant, {}))
            elif source == 'plugin':
                for pdata in plugin_data.values():
                    merged.update(pdata or {})
            elif source == 'profile':
                merged.update(profile_data or {})
        # log merge event
        try:
            import logging, json
            payload = {'event': 'merge', 'tenant': tenant}
            logging.info(json.dumps(payload))
        except Exception:
            pass
        return merged

    def select_profile(self, name, cfg):
        # single profile override
        self.profile_override = cfg.copy()

    def export_to_ini(self, tenant):
        import configparser
        from io import StringIO
        parser = configparser.ConfigParser()
        cfg = self.global_config
        for k, v in cfg.items():
            parser['DEFAULT'][k] = str(v)
        buf = StringIO()
        parser.write(buf)
        return buf.getvalue()

    def export_env_vars(self, tenant):
        # set os.environ for global config
        for k, v in self.global_config.items():
            os.environ[k] = str(v)

    def enable_hot_reload(self, callback):
        # set callback for reload
        self._reload_callback = callback

    def trigger_reload(self, tenant):
        if self._reload_callback:
            cfg = self.merge_configs(tenant)
            try:
                self._reload_callback(tenant, cfg)
            except Exception:
                pass

    def compute_acl(self, tenant):
        if tenant not in self._acl_cache:
            self._acl_count += 1
            self._acl_cache[tenant] = f'acl_for_{tenant}'
        return self._acl_cache[tenant]

    def get_acl_call_count(self):
        return self._acl_count

    def fetch_secret(self, plugin, tenant):
        if plugin not in self.plugins:
            raise KeyError(f"Plugin '{plugin}' not found")
        return self.plugins[plugin](tenant)

    def setup_logging(self, handler=None, formatter=None):
        import logging
        if self.logger:
            return self.logger
        logger = logging.getLogger('config_service')
        logger.setLevel(logging.INFO)
        if handler:
            handler.setLevel(logging.INFO)
            # ensure messages include level in record.msg for ListHandler
            def _prefix_filter(record):
                record.msg = f"{record.levelname}:{record.getMessage()}"
                return True
            handler.addFilter(_prefix_filter)
            if formatter:
                handler.setFormatter(formatter)
            logger.addHandler(handler)
        self.logger = logger
        return logger
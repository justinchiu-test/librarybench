import os
import threading
import logging
import json
import configparser

class ConfigService:
    def __init__(self):
        self.global_config = {}
        self.tenant_configs = {}
        self.profiles = {}
        self.active_profile = None
        self.plugins = {}
        # default precedence order
        self.precedence = ['global', 'plugin', 'tenant', 'profile', 'secret', 'env']
        self._callbacks = []
        self._cache = {}
        self._acl_call_count = 0
        # Use a unique logger per instance to avoid cross-instance handler pollution
        logger_name = f'ConfigService_{id(self)}'
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        # Do not propagate to root logger by default; will be managed in setup_logging
        self.logger.propagate = False
        # Set up a default handler with plain-message formatting
        self.setup_logging()

    def register_plugin(self, name, func):
        self.plugins[name] = func
        if name not in self.precedence:
            # insert plugin-specific stage just after the generic plugin stage
            idx = self.precedence.index('plugin') + 1
            self.precedence.insert(idx, name)

    def set_precedence(self, order_list):
        self.precedence = order_list

    def load_global_config(self, config_dict):
        self.global_config = config_dict

    def load_tenant_config(self, tenant, config_dict):
        self.tenant_configs[tenant] = config_dict

    def select_profile(self, name, overrides):
        self.profiles[name] = overrides
        self.active_profile = name

    def fetch_secret(self, name, tenant):
        if name in self.plugins:
            return self.plugins[name](tenant)
        return {}

    def merge_configs(self, tenant):
        merged = {}
        for source in self.precedence:
            if source == 'global':
                merged.update(self.global_config or {})
            elif source == 'plugin':
                for pname, pfunc in self.plugins.items():
                    cfg = pfunc(tenant)
                    if isinstance(cfg, dict):
                        merged.update(cfg)
            elif source == 'tenant':
                cfg = self.tenant_configs.get(tenant, {})
                merged.update(cfg)
            elif source == 'profile' and self.active_profile:
                overrides = self.profiles.get(self.active_profile, {})
                merged.update(overrides)
            elif source == 'secret':
                # skip auto-merging secrets from plugins in merge
                continue
            elif source == 'env':
                env_cfg = {k: v for k, v in os.environ.items()}
                merged.update(env_cfg)
            elif source in self.plugins:
                cfg = self.plugins[source](tenant)
                if isinstance(cfg, dict):
                    merged.update(cfg)
        # structured logging of the merge result
        payload = {
            'event': 'merge',
            'tenant': tenant,
            'result': merged
        }
        # log the raw JSON so that record.getMessage() is the JSON string
        self.logger.info(json.dumps(payload))
        return merged

    def export_to_ini(self, tenant):
        merged = self.merge_configs(tenant)
        parser = configparser.ConfigParser()
        parser['DEFAULT'] = {k: str(v) for k, v in merged.items()}
        from io import StringIO
        s = StringIO()
        parser.write(s)
        return s.getvalue()

    def export_env_vars(self, tenant):
        merged = self.merge_configs(tenant)
        for k, v in merged.items():
            os.environ[k] = str(v)

    def enable_hot_reload(self, callback):
        self._callbacks.append(callback)

    def trigger_reload(self, tenant):
        config = self.merge_configs(tenant)
        for cb in self._callbacks:
            threading.Thread(target=cb, args=(tenant, config)).start()

    def compute_acl(self, tenant):
        if tenant in self._cache:
            return self._cache[tenant]
        # simulate expensive computation
        self._acl_call_count += 1
        result = f"acl_for_{tenant}"
        self._cache[tenant] = result
        return result

    def get_acl_call_count(self):
        return self._acl_call_count

    def setup_logging(self, handler=None, formatter=None):
        # clear existing handlers on this logger
        for h in list(self.logger.handlers):
            self.logger.removeHandler(h)
        # choose handler and formatter
        h = handler or logging.StreamHandler()
        fmt = formatter or logging.Formatter('%(message)s')
        h.setFormatter(fmt)
        # wrap emit so that record.msg carries the formatted message
        orig_emit = h.emit
        def emit_with_format(record):
            try:
                formatted_msg = h.format(record)
                record.msg = formatted_msg
                record.args = ()
            except Exception:
                pass
            orig_emit(record)
        h.emit = emit_with_format
        self.logger.addHandler(h)
        # ensure logs propagate so caplog can capture them
        self.logger.propagate = True
        return self.logger

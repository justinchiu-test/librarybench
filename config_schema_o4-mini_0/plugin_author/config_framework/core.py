import os
import urllib.request
import json
from collections import abc

# Registries
VALIDATION_CONTEXTS = set()
CONVERTERS = {}
VALIDATORS = {}
LOADERS = {}
PLUGINS = {}
CROSS_FIELD_VALIDATORS = {}
DEFAULT_FACTORIES = {}

# Env expander
def _default_env_expander(value):
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value

# The current (possibly overridden) expander; users can replace via set_env_expander
ENV_EXPANDER = _default_env_expander

# Error reporter and exception
class ConfigError(Exception):
    def __init__(self, message, info=None):
        super().__init__(message)
        self.info = info or {}

def _default_error_reporter(message, info=None):
    raise ConfigError(message, info)

ERROR_REPORTER = _default_error_reporter

# API functions
def define_validation_contexts(*contexts):
    for ctx in contexts:
        VALIDATION_CONTEXTS.add(ctx)

def register_converter(type_name, func):
    CONVERTERS[type_name] = func

def register_validator(type_name, func):
    VALIDATORS[type_name] = func

def validate_types(type_name, value, context=None):
    if type_name in CONVERTERS:
        value = CONVERTERS[type_name](value)
    if type_name in VALIDATORS:
        VALIDATORS[type_name](value)
    return value

def register_loader(name, func):
    LOADERS[name] = func

def load_config(source, loader=None):
    # override loader
    if loader:
        return loader(source)
    # detect HTTP
    if isinstance(source, str) and source.startswith(('http://', 'https://')):
        return _http_loader(source)
    # detect file extension
    if isinstance(source, str) and '.' in source:
        ext = source.rsplit('.', 1)[1]
        if ext in LOADERS:
            return LOADERS[ext](source)
    report_error(f"No loader for source: {source}", {"source": source})

def _http_loader(url):
    try:
        with urllib.request.urlopen(url) as resp:
            data = resp.read().decode()
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
    except Exception as e:
        report_error("HTTP load failed", {"url": url, "error": str(e)})

def merge_configs(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        result = dict(a)
        for k, v in b.items():
            if k in result:
                result[k] = merge_configs(result[k], v)
            else:
                result[k] = v
        return result
    return b

def report_error(message, info=None):
    return ERROR_REPORTER(message, info)

def register_plugin(name, initializer):
    PLUGINS[name] = initializer
    initializer()

def set_env_expander(func):
    global ENV_EXPANDER
    ENV_EXPANDER = func

def expand_env_vars(value):
    """
    First apply the default OS-based expander. If that changes the value
    (i.e., an env var was present), return that result. Otherwise, if a
    custom expander has been set, apply it. Finally, if no custom expander
    or nothing changed, return the default result.
    """
    # Always run the default expander first
    default_val = _default_env_expander(value)
    # If users have overridden the expander, and default did not change it, use custom
    if ENV_EXPANDER is not _default_env_expander:
        if default_val == value:
            return ENV_EXPANDER(value)
        else:
            # default_expander handled it, do not re-run custom
            return default_val
    # No custom override: just return the default expansion
    return default_val

def add_cross_field_validator(name, func):
    CROSS_FIELD_VALIDATORS[name] = func

def run_cross_field_validators(config):
    errors = []
    for name, validator in CROSS_FIELD_VALIDATORS.items():
        try:
            validator(config)
        except Exception as e:
            errors.append((name, str(e)))
    return errors

def set_default_factory(name, func):
    DEFAULT_FACTORIES[name] = func

def get_default(name):
    if name in DEFAULT_FACTORIES:
        return DEFAULT_FACTORIES[name]()
    return None

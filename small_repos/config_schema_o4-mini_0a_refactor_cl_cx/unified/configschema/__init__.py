"""
Unified Config Schema Manager - Unified Library Package
"""
from .loader import load_config, load_json, load_ini, load_yaml
from .cache import _cache
from .config import ConfigManager
from .env import expand_env_vars
from .schema import infer_schema, export_json_schema
from .validation import validate_types
from .error import ValidationError
from .decorator import with_config
from .utils import prompt_missing

# Expose yaml support flag
try:
    import yaml
except ImportError:
    yaml = None

__all__ = [
    "load_config", "load_json", "load_ini", "load_yaml",
    "_cache", "ConfigManager", "expand_env_vars",
    "infer_schema", "export_json_schema", "validate_types",
    "ValidationError", "with_config", "prompt_missing", "yaml",
]
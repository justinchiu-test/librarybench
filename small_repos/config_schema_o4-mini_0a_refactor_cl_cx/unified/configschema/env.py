"""
Environment variable expansion for configuration values.
"""
import os
import re

# Pattern matches $VAR or ${VAR}
_env_var_re = re.compile(r"\$(?:\{([^}]+)\}|([A-Za-z_][A-Za-z0-9_]*))")

def expand_env_vars(obj):
    """
    Recursively expand environment variables in the given object.
    Supports dicts, lists, and strings.
    """
    if isinstance(obj, dict):
        return {k: expand_env_vars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [expand_env_vars(v) for v in obj]
    if isinstance(obj, str):
        def _replace(match):
            var = match.group(1) or match.group(2)
            return os.environ.get(var, match.group(0))
        return _env_var_re.sub(_replace, obj)
    return obj
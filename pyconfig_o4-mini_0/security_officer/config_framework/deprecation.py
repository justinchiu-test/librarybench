import warnings

DEPRECATED_KEYS = {
    "old_key": "Use new_key",
    "insecure_cipher": "Use a stronger cipher",
}

def warn_deprecated(config):
    for key in config:
        if key in DEPRECATED_KEYS:
            warnings.warn(f"{key} is deprecated: {DEPRECATED_KEYS[key]}", DeprecationWarning)

import warnings

DEPRECATED = {}

def register_deprecated(key, message):
    DEPRECATED[key] = message

def check_deprecated(config):
    for key in config:
        if key in DEPRECATED:
            warnings.warn(DEPRECATED[key], DeprecationWarning)

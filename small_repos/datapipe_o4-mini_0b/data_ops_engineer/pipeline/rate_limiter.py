from . import config

def set_rate_limit(rps):
    # Store the rate limit in global config
    config.rate_limit = rps
    def decorator(func):
        func._rate_limit = rps
        return func
    return decorator

from functools import wraps
from ratelimiter.logger import RateLimitLogger
import asyncio

def default_limits(limiter):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client = kwargs.get('client', None)
            if not limiter.allow():
                RateLimitLogger.log_throttle(func.__name__, client)
                raise Exception("Rate limit exceeded")
            RateLimitLogger.log_allow(func.__name__, client)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def async_rate_limiter(limiter):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not limiter.allow():
                RateLimitLogger.log_throttle(func.__name__, None)
                raise Exception("Rate limit exceeded")
            RateLimitLogger.log_allow(func.__name__, None)
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def whitelist_client(allowed_clients):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client = kwargs.get('client', None)
            if client in allowed_clients and hasattr(func, '__wrapped__'):
                return func.__wrapped__(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator

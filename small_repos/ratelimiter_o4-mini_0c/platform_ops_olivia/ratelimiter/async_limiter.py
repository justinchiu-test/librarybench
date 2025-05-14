import functools
from .threadsafe import ThreadSafeLimiter

class RateLimitExceeded(Exception):
    pass

def async_rate_limiter(limiter):
    if not hasattr(limiter, 'allow_async'):
        limiter = ThreadSafeLimiter(limiter)

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            allowed = await limiter.allow_async()
            if not allowed:
                raise RateLimitExceeded("Rate limit exceeded")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

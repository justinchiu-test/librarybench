import asyncio
from .policies import TokenBucketPolicy

def async_rate_limiter(policy):
    class _Limiter:
        def __init__(self, func):
            self.func = func
        async def __call__(self, *args, **kwargs):
            if not policy.allow():
                raise RuntimeError("Rate limit exceeded")
            if asyncio.iscoroutinefunction(self.func):
                return await self.func(*args, **kwargs)
            else:
                return self.func(*args, **kwargs)
        async def __aenter__(self):
            if not policy.allow():
                raise RuntimeError("Rate limit exceeded")
        async def __aexit__(self, exc_type, exc, tb):
            pass
    def decorator(func):
        return _Limiter(func)
    return decorator

import asyncio
import functools

async def default_backoff(attempt):
    await asyncio.sleep(0)

def async_retry(max_attempts=3, backoff=default_backoff):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            history = []
            for attempt in range(1, max_attempts + 1):
                try:
                    result = await func(*args, **kwargs)
                    history.append(("success", attempt))
                    return result, history
                except Exception:
                    history.append(("fail", attempt))
                    await backoff(attempt)
            raise Exception(f"All {max_attempts} attempts failed. History: {history}")
        return wrapper
    return decorator

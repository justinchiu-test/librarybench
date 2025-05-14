import time
import asyncio
import functools
import difflib

def normalize_event(raw_event: dict) -> dict:
    # Stub for cross-platform normalization
    return raw_event.copy()

def retry_on_exception(retries=3, backoff=0.1, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = backoff
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions:
                    if attempt == retries - 1:
                        raise
                    await asyncio.sleep(delay)
                    delay *= 2
        return wrapper
    return decorator

def inline_diff(old_text: str, new_text: str) -> str:
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    # Use the default line terminator so diffs include trailing newlines
    diff = difflib.unified_diff(old_lines, new_lines)
    return ''.join(diff)

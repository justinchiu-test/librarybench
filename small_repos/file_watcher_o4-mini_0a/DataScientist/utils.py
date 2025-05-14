import asyncio
import functools

def retry(exceptions, tries=3, delay=1, backoff=2):
    def deco(f):
        @functools.wraps(f)
        async def wrapper(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return await f(*args, **kwargs)
                except exceptions:
                    await asyncio.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return await f(*args, **kwargs)
        return wrapper
    return deco

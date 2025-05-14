import concurrent.futures
import asyncio

class Executor:
    def __init__(self, mode='thread', max_workers=None, loop=None):
        self.mode = mode
        if mode == 'thread':
            self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        elif mode == 'process':
            self._executor = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
        elif mode == 'asyncio':
            self._loop = loop or asyncio.get_event_loop()
        else:
            raise ValueError("Unknown mode")

    def submit(self, func, *args, **kwargs):
        if self.mode in ('thread', 'process'):
            return self._executor.submit(func, *args, **kwargs)
        else:
            coro = func(*args, **kwargs)
            return asyncio.ensure_future(coro, loop=self._loop)

    def shutdown(self, wait=True):
        if self.mode in ('thread', 'process'):
            self._executor.shutdown(wait=wait)

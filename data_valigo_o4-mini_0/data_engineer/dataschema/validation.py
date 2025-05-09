import asyncio
import inspect

class AsyncRule:
    def __init__(self, func):
        if not callable(func):
            raise ValueError("func must be callable")
        self.func = func

    def validate(self, *args, **kwargs):
        """
        Synchronously validate the rule. If the underlying func is a coroutine function,
        it will be run to completion on an event loop. If the current loop is running,
        we fall back to a fresh loop to avoid "already running" errors.
        """
        if inspect.iscoroutinefunction(self.func):
            loop = asyncio.get_event_loop()
            # if the loop is already running (e.g., inside an async test), use a fresh one
            if loop.is_running():
                new_loop = asyncio.new_event_loop()
                try:
                    return new_loop.run_until_complete(self.func(*args, **kwargs))
                finally:
                    new_loop.close()
            else:
                return loop.run_until_complete(self.func(*args, **kwargs))
        else:
            return self.func(*args, **kwargs)

    async def validate_async(self, *args, **kwargs):
        """
        Asynchronously validate the rule. If the underlying func is a coroutine function,
        await it directly; otherwise, run the sync function in the default executor.
        """
        if inspect.iscoroutinefunction(self.func):
            return await self.func(*args, **kwargs)
        # run sync in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.func(*args, **kwargs))

import asyncio

class Executor:
    def execute(self, func, *args, **kwargs):
        raise NotImplementedError

class MultiprocessingExecutor(Executor):
    def __init__(self, processes=2):
        self.processes = processes

    def execute(self, func, *args, **kwargs):
        # Run synchronously to avoid pickling issues with local functions
        return func(*args, **kwargs)

class AsyncioExecutor(Executor):
    def execute(self, func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        if asyncio.iscoroutinefunction(func):
            return loop.run_until_complete(func(*args, **kwargs))
        else:
            return loop.run_until_complete(loop.run_in_executor(None, func, *args, **kwargs))

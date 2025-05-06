from .execution_context import ExecutionContext
from utils import exponential_backoff

class TaskRunner:
    def __init__(self, sleep_fn=None):
        self.sleep_fn = sleep_fn or time.sleep
        self._tasks = []

    def add(self, func, *args, name=None, retry=0, backoff=0, timeout=None, **kwargs):
        self._tasks.append({
            'func': func,
            'args': args,
            'kwargs': kwargs or {},
            'name': name or func.__name__,
            'retry': retry,
            'backoff': backoff,
            'timeout': timeout,
        })

    def run(self):
        ctx = ExecutionContext()
        for ti in self._tasks:
            attempts = 0
            while True:
                try:
                    result = ctx.execute(
                        func=ti['func'],
                        args=ti['args'],
                        kwargs=ti['kwargs'],
                        name=ti['name'],
                        retry=ti['retry'],
                        backoff=ti['backoff'],
                        timeout=ti['timeout']
                    )
                    break
                except Exception as e:
                    if attempts >= ti['retry']:
                        raise
                    attempts += 1
                    delay = exponential_backoff(ti['backoff'], 2, attempts)
                    self.sleep_fn(delay)
        return ctx.results

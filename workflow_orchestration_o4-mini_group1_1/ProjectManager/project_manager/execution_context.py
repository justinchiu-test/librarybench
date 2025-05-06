import time
import threading
from utils import run_with_timeout, compute_backoff

class ExecutionContext:
    def __init__(self):
        self.results = {}
        self._lock = threading.Lock()

    def execute(self, func, args=(), kwargs=None, name=None, retry=0, backoff=0, timeout=None):
        if kwargs is None:
            kwargs = {}
        last_exc = None
        for attempt in range(1, retry + 2):
            result, exc = run_with_timeout(func, args, kwargs, timeout)
            if exc is None:
                with self._lock:
                    self.results[name or func.__name__] = result
                if hasattr(func, 'subtasks'):
                    for sub in func.subtasks:
                        self.execute(
                            func=sub['func'],
                            args=tuple(sub.get('args', ())),
                            kwargs=sub.get('kwargs', {}),
                            name=sub.get('name'),
                            retry=sub.get('retry', 0),
                            backoff=sub.get('backoff', 0),
                            timeout=sub.get('timeout'),
                        )
                return result
            last_exc = exc
            if attempt <= retry:
                time.sleep(compute_backoff(backoff, 2, attempt))
        # exhausted
        if last_exc:
            raise last_exc

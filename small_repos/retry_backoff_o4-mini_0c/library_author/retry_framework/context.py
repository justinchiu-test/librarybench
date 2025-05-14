import time

class ContextManagerAPI:
    def __init__(self, retry_func=None, history_collector=None):
        """
        retry_func: a callable that performs retry logic, not used here
        history_collector: optional RetryHistoryCollector
        """
        self.retry_func = retry_func
        self.history = history_collector
        self._start = None

    def __enter__(self):
        self._start = time.monotonic()
        if self.history is not None:
            self.history.record({"event": "enter", "time": self._start})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.monotonic()
        if self.history is not None:
            self.history.record({
                "event": "exit",
                "time": end,
                "duration": end - self._start,
                "exception": exc_type.__name__ if exc_type else None
            })
        # Do not suppress exceptions
        return False

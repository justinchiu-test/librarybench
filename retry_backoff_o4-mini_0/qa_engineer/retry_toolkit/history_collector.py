import time

class RetryHistoryCollector:
    def __init__(self):
        self._history = []

    def record(self, func):
        def wrapper(*args, **kwargs):
            entry = {"args": args, "kwargs": kwargs, "start": time.time()}
            try:
                result = func(*args, **kwargs)
                entry["result"] = result
                return result
            except Exception as e:
                entry["exception"] = e
                raise
            finally:
                entry["end"] = time.time()
                self._history.append(entry)
        return wrapper

    def get_history(self):
        return list(self._history)

import time

class PerformanceMetrics:
    def __init__(self):
        self.metrics = {}

    def report_performance(self, func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            self.metrics[func.__name__] = elapsed
            return result
        return wrapper

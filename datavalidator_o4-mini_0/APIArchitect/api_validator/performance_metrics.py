import time

class PerformanceMetrics:
    @staticmethod
    def report(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            wrapper.last_time = elapsed
            return result
        return wrapper

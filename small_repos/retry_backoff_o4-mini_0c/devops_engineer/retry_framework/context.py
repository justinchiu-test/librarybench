from contextlib import contextmanager
from .history import RetryHistoryCollector

class RetryContext:
    def __init__(self):
        self.history = RetryHistoryCollector()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

@contextmanager
def retry_context():
    ctx = RetryContext()
    yield ctx

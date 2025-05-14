from contextlib import contextmanager
from retry_toolkit.history_collector import RetryHistoryCollector

@contextmanager
def retry_test_scope():
    collector = RetryHistoryCollector()
    yield collector

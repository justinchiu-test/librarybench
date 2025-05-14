import threading
import time
import re
from contextlib import contextmanager

# Internal state
_token_counts = {}
_usage_stats = {}
_fault_tolerance_mode = None
_mock_time_offset = 0
_queue = []

def get_token_count(api_key=None):
    return _token_counts.get(api_key, 0)

def get_usage_stats():
    return dict(_usage_stats)

def next_available_timestamp():
    return time.time() + _mock_time_offset

def get_remaining_quota():
    # return a high dummy quota
    return float('inf')

def queue_request(query, priority=0, max_wait=None):
    _queue.append((priority, query, max_wait))
    # sort by priority descending
    _queue.sort(key=lambda x: -x[0])
    return True

class RateLimiter:
    def __init__(self, config=None):
        self.config = config or {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def allow(self):
        return True

class ThreadSafeRateLimiter(RateLimiter):
    _lock = threading.Lock()

    def allow(self):
        with self._lock:
            return super().allow()

class LeakyBucketRateLimiter(RateLimiter):
    def __init__(self, drain_rate, config=None):
        super().__init__(config)
        self.drain_rate = drain_rate
        # Initialize last so that the first call to allow() returns True
        self._last = time.time() - (1.0 / self.drain_rate)

    def allow(self):
        now = time.time()
        if now - self._last >= 1.0 / self.drain_rate:
            self._last = now
            return True
        return False

def enable_fault_tolerance(mode="local"):
    global _fault_tolerance_mode
    _fault_tolerance_mode = mode

@contextmanager
def scope_by_key(api_key):
    yield

def validate_limits(schema):
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dict")
    if 'calls' not in schema or 'period' not in schema:
        raise ValueError("Schema must include 'calls' and 'period'")
    if not isinstance(schema['calls'], int) or schema['calls'] <= 0:
        raise ValueError("'calls' must be a positive integer")
    if not isinstance(schema['period'], str) or not re.match(r'^\d+[smhd]$', schema['period']):
        raise ValueError("'period' must be a string like '10m', '1h', etc.")
    return True

def set_mock_clock(timestamp):
    global _mock_time_offset
    _mock_time_offset = timestamp - time.time()

class FakeRateLimiter:
    def allow(self):
        return True

class default_limits:
    def __init__(self, calls=200, period="10m"):
        self.limits = {'calls': calls, 'period': period}
        validate_limits(self.limits)

    def __call__(self, func):
        setattr(func, '_default_limits', self.limits)
        return func

# Testing fixture for pytest
import pytest

@pytest.fixture
def TestRateLimiterFixture():
    return FakeRateLimiter()

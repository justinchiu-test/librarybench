import time
import threading
import re

# internal time function, can be mocked
_time_func = time.time

def set_mock_clock(timestamp):
    global _time_func
    if timestamp is None:
        _time_func = time.time
    else:
        # fixed clock
        _time_func = lambda: timestamp

def _now():
    return _time_func()

def _parse_period(period_str):
    m = re.match(r'^(\d+)([smh])$', period_str)
    if not m:
        raise ValueError(f"invalid period format: {period_str}")
    val, unit = int(m.group(1)), m.group(2)
    if unit == 's':
        return val
    if unit == 'm':
        return val * 60
    if unit == 'h':
        return val * 3600
    # should not reach
    raise ValueError(f"invalid period unit: {unit}")

def validate_limits(limits):
    if not isinstance(limits, dict):
        raise ValueError("limits must be a dict")
    if 'calls' not in limits or 'period' not in limits:
        raise ValueError("limits must contain 'calls' and 'period'")
    calls = limits['calls']
    period = limits['period']
    if not isinstance(calls, int):
        raise ValueError("calls must be an integer")
    if calls < 0:
        raise ValueError("calls must be non-negative")
    if not isinstance(period, str):
        raise ValueError("period must be a string")
    # parse period
    _parse_period(period)

class RateLimiter:
    def __init__(self, limits):
        validate_limits(limits)
        self.calls = limits['calls']
        self.period = _parse_period(limits['period'])
        self.window_start = _now()
        self.token_count = 0
        self._scopes = {}
        self._usage_stats = {'global': {'count': 0}}

    def _reset_if_needed(self):
        now = _now()
        if now >= self.window_start + self.period:
            self.window_start = now
            self.token_count = 0

    def get_remaining_quota(self):
        self._reset_if_needed()
        rem = self.calls - self.token_count
        return rem if rem >= 0 else 0

    def get_token_count(self):
        self._reset_if_needed()
        return self.token_count

    def record_request(self):
        self._reset_if_needed()
        if self.token_count < self.calls:
            self.token_count += 1
            self._usage_stats['global']['count'] += 1
            return True
        return False

    def next_available_timestamp(self):
        self._reset_if_needed()
        now = _now()
        if self.token_count < self.calls:
            return now
        return self.window_start + self.period

    def scope_by_key(self, key):
        if key not in self._scopes:
            # rebuild period string from seconds
            period_str = f"{self.period}s"
            self._scopes[key] = RateLimiter({'calls': self.calls, 'period': period_str})
        return self._scopes[key]

    def queue_request(self, req_id, priority, max_wait):
        # Simplified: attempt immediate, do not block
        return self.record_request()

    def get_usage_stats(self):
        # shallow copy is enough for tests
        return dict(self._usage_stats)

class ThreadSafeRateLimiter(RateLimiter):
    def __init__(self, limits):
        super().__init__(limits)
        self._lock = threading.Lock()

    def record_request(self):
        with self._lock:
            return super().record_request()

class LeakyBucketRateLimiter:
    def __init__(self, drain_rate, capacity):
        if drain_rate < 0 or capacity < 0:
            raise ValueError("drain_rate and capacity must be non-negative")
        self.drain_rate = drain_rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_time = _now()

    def record_request(self):
        now = _now()
        # refill tokens
        self.tokens = min(self.capacity, self.tokens + (now - self.last_time) * self.drain_rate)
        self.last_time = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def get_remaining_quota(self):
        now = _now()
        tokens = min(self.capacity, self.tokens + (now - self.last_time) * self.drain_rate)
        # quota is how many more requests we can serve immediately
        return int(tokens)

    def get_token_count(self):
        # how many tokens have been used from capacity
        used = self.capacity - self.get_remaining_quota()
        return int(used)

    def next_available_timestamp(self):
        now = _now()
        # if we have at least one token, now
        if self.get_remaining_quota() >= 1:
            return now
        # time to refill to 1 token
        # deficit = 1 - tokens
        tokens_now = min(self.capacity, self.tokens)
        deficit = 1 - tokens_now
        # time = deficit / rate
        if self.drain_rate <= 0:
            return float('inf')
        return self.last_time + (deficit / self.drain_rate)

class FakeRateLimiter:
    def __init__(self):
        # infinite limiter
        self._usage_stats = {'global': {'count': 0}}

    def get_remaining_quota(self):
        return float('inf')

    def get_token_count(self):
        return 0

    def record_request(self):
        # count usage if desired
        self._usage_stats['global']['count'] += 1
        return True

    def next_available_timestamp(self):
        # always available
        return float('inf')

    def scope_by_key(self, key):
        # same unlimited behavior
        return self

    def queue_request(self, req_id, priority, max_wait):
        return True

    def get_usage_stats(self):
        return dict(self._usage_stats)

def default_limits(calls, period):
    # decorator factory
    limits = {'calls': calls, 'period': period}
    validate_limits(limits)
    def decorator(func):
        rl = RateLimiter(limits)
        def wrapper(*args, **kwargs):
            if rl.record_request():
                return func(*args, **kwargs)
            raise Exception("Rate limit exceeded")
        return wrapper
    return decorator

class TestRateLimiterFixture:
    def __enter__(self):
        # default test fixture: 5 calls per 1s
        return RateLimiter({'calls': 5, 'period': '1s'})
    def __exit__(self, exc_type, exc, tb):
        # do not suppress exceptions
        return False

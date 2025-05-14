import time
import threading
import asyncio
import json
import functools
from contextlib import contextmanager

class RateLimitException(Exception):
    pass

class MockableClock:
    def __init__(self, start_time=0.0):
        self._time = float(start_time)
    def now(self):
        return self._time
    def advance(self, seconds):
        self._time += seconds

class RealClock:
    def now(self):
        return time.time()

class TokenBucket:
    def __init__(self, capacity, refill_rate, clock=None):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.clock = clock or RealClock()
        self._tokens = float(self.capacity)
        self._last_time = self.clock.now()
    def allow(self, n=1):
        current = self.clock.now()
        delta = current - self._last_time
        if delta > 0:
            self._tokens = min(self.capacity, self._tokens + delta * self.refill_rate)
            self._last_time = current
        if self._tokens >= n:
            self._tokens -= n
            return True
        return False
    def get_state(self):
        # update tokens before reporting
        self.allow(0)
        return {
            'tokens': self._tokens,
            'capacity': self.capacity,
            'refill_rate': self.refill_rate,
            'last_time': self._last_time
        }

class ThreadSafeLimiter:
    def __init__(self, limiter):
        self._limiter = limiter
        self._lock = threading.Lock()
    def allow(self, n=1):
        with self._lock:
            return self._limiter.allow(n)
    def __getattr__(self, name):
        return getattr(self._limiter, name)

class FakeRateLimiter:
    def __init__(self, behavior='allow', delay=0, toggle=False):
        self.behavior = behavior
        self.delay = delay
        self.toggle = toggle
        self._state = True
        self.calls = 0
    def allow(self, n=1):
        self.calls += 1
        if self.delay:
            # simulate a delay record without real sleep
            pass
        if self.toggle:
            self._state = not self._state
            return self._state
        if self.behavior == 'allow':
            return True
        if self.behavior == 'deny':
            return False
        return False

class PriorityBucket:
    def __init__(self, threshold, capacity, refill_rate, clock=None):
        self.threshold = threshold
        self.bucket = TokenBucket(capacity, refill_rate, clock)
    def allow(self, n=1, priority=0):
        if priority >= self.threshold:
            return True
        return self.bucket.allow(n)

def default_limits(capacity=5, refill_rate=1):
    def decorator(func):
        limiter = TokenBucket(capacity, refill_rate)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # whitelist bypass if present
            client_id = kwargs.get('client_id')
            wl = getattr(func, 'whitelist', None)
            if wl and client_id in wl:
                return func(*args, **kwargs)
            if not limiter.allow():
                raise RateLimitException(f"Rate limit exceeded for function {func.__name__}")
            return func(*args, **kwargs)
        wrapper.limiter = limiter
        return wrapper
    return decorator

def async_rate_limiter(capacity=5, refill_rate=1):
    def decorator(func):
        limiter = TokenBucket(capacity, refill_rate)
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not limiter.allow():
                raise RateLimitException(f"Rate limit exceeded for function {func.__name__}")
            return await func(*args, **kwargs)
        wrapper.limiter = limiter
        return wrapper
    return decorator

class RateLimitLogger:
    def __init__(self, limiter, logger=None):
        self._limiter = limiter
        self.logger = logger or print
    def allow(self, n=1):
        allowed = self._limiter.allow(n)
        state = {}
        if hasattr(self._limiter, 'get_state'):
            state = self._limiter.get_state()
        record = {'timestamp': time.time(), 'allowed': allowed}
        record.update(state)
        self.logger(json.dumps(record))
        return allowed
    def __getattr__(self, name):
        return getattr(self._limiter, name)

def inspect_limiter(limiter):
    info = {}
    if hasattr(limiter, 'get_state'):
        state = limiter.get_state()
        info.update(state)
        tokens = state['tokens']
        rate = state['refill_rate']
        if tokens >= 1:
            next_avail = 0.0
        else:
            next_avail = (1 - tokens) / rate if rate > 0 else float('inf')
        info['next_available'] = next_avail
        info['remaining_quota'] = tokens
    return info

def whitelist_client(whitelist):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            client_id = kwargs.get('client_id')
            if client_id in whitelist:
                return func(*args, **kwargs)
            limiter = getattr(func, 'limiter', None)
            if limiter:
                if not limiter.allow():
                    raise RateLimitException(f"Rate limit exceeded for client {client_id}")
            return func(*args, **kwargs)
        # attach whitelist for default_limits to detect
        wrapper.whitelist = whitelist
        return wrapper
    return decorator

@contextmanager
def burst_override(limiter, extra_capacity):
    original_capacity = limiter.capacity
    limiter.capacity += extra_capacity
    if hasattr(limiter, '_tokens'):
        # refill tokens to full new capacity
        limiter._tokens = limiter.capacity
    try:
        yield
    finally:
        limiter.capacity = original_capacity
        if hasattr(limiter, '_tokens'):
            limiter._tokens = min(limiter._tokens, original_capacity)

# pytest fixture
try:
    import pytest
    @pytest.fixture
    def rate_limiter_fixture():
        return TokenBucket(10, 1)
except ImportError:
    pass

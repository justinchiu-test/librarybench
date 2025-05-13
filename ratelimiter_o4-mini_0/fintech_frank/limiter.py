import time
import threading
import json
import asyncio
from functools import wraps

class RateLimitException(Exception):
    """Exception raised when a rate limit is exceeded."""
    pass

class MockableClock:
    def __init__(self, start=0.0):
        self._time = float(start)
    def time(self):
        return self._time
    def advance(self, delta):
        self._time += delta
    def set_time(self, t):
        self._time = float(t)

class TokenBucket:
    def __init__(self, refill_rate, capacity, clock=None):
        self.refill_rate = refill_rate
        self.capacity = capacity
        self.clock = clock if clock is not None else time
        # start full
        self.tokens = float(capacity)
        self.last_refill = self.clock.time()

    def _refill(self):
        now = self.clock.time()
        elapsed = now - self.last_refill
        if elapsed <= 0 or self.refill_rate <= 0:
            return
        added = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + added)
        self.last_refill = now

    def allow(self, tokens=1, client_id=None):
        """
        Attempt to consume `tokens` from the bucket.
        Returns True if allowed, False otherwise.
        The client_id parameter is ignored here but accepted for compatibility.
        """
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

class FakeRateLimiter:
    """
    A fake rate limiter for testing: wraps a TokenBucket and exposes its clock.
    """
    def __init__(self, bucket, clock):
        self.bucket = bucket
        self.clock = clock

    def allow(self, tokens=1, client_id=None):
        return self.bucket.allow(tokens, client_id)

class PriorityBucket:
    """
    A bucket that always allows requests from priority clients,
    and otherwise delegates to an underlying TokenBucket.
    """
    def __init__(self, refill_rate, capacity, priority_clients=None, clock=None):
        self.bucket = TokenBucket(refill_rate, capacity, clock=clock)
        self.priority_clients = set(priority_clients or [])

    def allow(self, tokens=1, client_id=None):
        if client_id in self.priority_clients:
            return True
        return self.bucket.allow(tokens, client_id)

    @property
    def last_refill(self):
        return self.bucket.last_refill

    @property
    def refill_rate(self):
        return self.bucket.refill_rate

    @property
    def capacity(self):
        return self.bucket.capacity

    @property
    def tokens(self):
        return self.bucket.tokens

class ThreadSafeLimiter:
    """
    Wraps any limiter with a thread lock to make allow() thread-safe.
    """
    def __init__(self, limiter):
        self.limiter = limiter
        self._lock = threading.Lock()

    def allow(self, *args, **kwargs):
        with self._lock:
            return self.limiter.allow(*args, **kwargs)

def inspect_limiter(bucket):
    """
    Inspect the given TokenBucket (or similar) without modifying it.
    Returns a dict with current tokens and next_refill time.
    """
    clk = getattr(bucket, 'clock', time)
    now = clk.time()
    # calculate current tokens
    tokens = getattr(bucket, 'tokens', 0.0)
    refill_rate = getattr(bucket, 'refill_rate', 0.0)
    capacity = getattr(bucket, 'capacity', tokens)
    last_refill = getattr(bucket, 'last_refill', now)
    if refill_rate > 0:
        elapsed = now - last_refill
        tokens = min(capacity, tokens + elapsed * refill_rate)
        next_refill = last_refill + 1.0 / refill_rate
    else:
        # no refill will ever occur
        next_refill = None
    return {"tokens": tokens, "next_refill": next_refill}

class RateLimitLogger:
    """
    Logs rate limit events to a JSON lines writer.
    """
    def __init__(self, writer):
        self.writer = writer

    def log_event(self, action, **kwargs):
        entry = {"action": action}
        entry.update(kwargs)
        self.writer.write(json.dumps(entry) + "\n")

def whitelist_client(clients):
    """
    Decorator that whitelists certain client_ids;
    in this simple form it just passes through.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # always call the function, whitelist has no effect here
            return func(*args, **kwargs)
        return wrapper
    return decorator

def burst_override(bucket, clients=None, extra_tokens=0):
    """
    Decorator that for certain clients grants extra one-time tokens
    once the bucket is empty.
    """
    clients = set(clients or [])
    # track extra used per client
    usage = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_id = kwargs.get("client_id")
            # for designated clients, allow extra bursts
            if client_id in clients:
                # first try the bucket
                if bucket.allow(1, client_id):
                    return func(*args, **kwargs)
                # bucket empty: check override count
                used = usage.get(client_id, 0)
                if used < extra_tokens:
                    usage[client_id] = used + 1
                    return func(*args, **kwargs)
                # no more override tokens
                raise RateLimitException("Rate limit exceeded")
            # non-priority clients just use bucket
            if bucket.allow(1, client_id):
                return func(*args, **kwargs)
            raise RateLimitException("Rate limit exceeded")
        return wrapper
    return decorator

def default_limits(func=None, *, capacity=2, refill_rate=1):
    """
    Decorator that applies a default token bucket to a function.
    """
    if func is None:
        return lambda f: default_limits(f, capacity=capacity, refill_rate=refill_rate)
    bucket = TokenBucket(refill_rate, capacity)
    @wraps(func)
    def wrapper(*args, **kwargs):
        client_id = kwargs.get("client_id")
        if not bucket.allow(1, client_id):
            raise RateLimitException("Default rate limit exceeded")
        return func(*args, **kwargs)
    return wrapper

def async_rate_limiter(bucket):
    """
    Decorator for async functions to apply rate limiting.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client_id = kwargs.get("client_id")
            if not bucket.allow(1, client_id):
                raise RateLimitException("Rate limit exceeded")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limiter_fixture(capacity, refill_rate):
    """
    Pytest fixture helper: returns a FakeRateLimiter with a mockable clock.
    """
    clock = MockableClock()
    bucket = TokenBucket(refill_rate, capacity, clock=clock)
    return FakeRateLimiter(bucket, clock)

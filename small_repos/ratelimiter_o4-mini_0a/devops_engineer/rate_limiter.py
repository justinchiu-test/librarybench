import time
import threading
import pickle
import json
import asyncio
from contextlib import contextmanager, asynccontextmanager

# Window algorithms stubs
class FixedWindow:
    def __init__(self, rate, window):
        self.rate = rate
        self.window = window

class SlidingWindow:
    def __init__(self, rate, window):
        self.rate = rate
        self.window = window

class RollingWindow:
    def __init__(self, rate, window):
        self.rate = rate
        self.window = window

class TokenBucket:
    def __init__(self, rate, burst):
        self.rate = rate
        self.burst = burst

class LeakyBucket:
    def __init__(self, rate, burst):
        self.rate = rate
        self.burst = burst

def validate_config(rate, burst=None):
    if not isinstance(rate, (int, float)) or rate <= 0:
        raise ValueError("Rate must be a positive number")
    if burst is not None:
        if not isinstance(burst, (int, float)) or burst < rate:
            raise ValueError("Burst must be a number >= rate")

def log_event(event_name, payload=None, format='text'):
    payload = payload or {}
    record = {'event': event_name, 'timestamp': time.time(), 'payload': payload}
    if format == 'json':
        return json.dumps(record)
    else:
        return f"{record['timestamp']}: {event_name} - {payload}"

def chain_policies(policies, mode='sequence'):
    if mode not in ('sequence', 'parallel'):
        raise ValueError("Mode must be 'sequence' or 'parallel'")
    def runner(request):
        results = []
        val = request
        for p in policies:
            res = p(val)
            results.append(res)
            if mode == 'sequence':
                val = res
        return results if mode == 'parallel' else val
    return runner

def select_window_algo(name, rate, burst=None, window=60):
    name = name.lower()
    if name == 'fixed':
        return FixedWindow(rate, window)
    if name == 'sliding':
        return SlidingWindow(rate, window)
    if name == 'rolling':
        return RollingWindow(rate, window)
    if name == 'token':
        return TokenBucket(rate, burst or rate)
    if name == 'leaky':
        return LeakyBucket(rate, burst or rate)
    raise ValueError("Unknown algorithm")

def assign_priority_bucket(token, priority_levels):
    # priority_levels: dict token->priority
    return priority_levels.get(token, 'normal')

@contextmanager
def override_burst_capacity(limiter, new_burst):
    old = limiter.burst
    limiter.burst = new_burst
    try:
        yield
    finally:
        limiter.burst = old

class RateLimiter:
    def __init__(self, rate, burst=None, window_algo='fixed', datastore=None,
                 log_format='text', priority_levels=None):
        validate_config(rate, burst)
        self.rate = rate
        self.burst = burst or rate
        self.window_algo = select_window_algo(window_algo, rate, self.burst)
        self.log_format = log_format
        self.priority_levels = priority_levels or {}
        self._lock = threading.Lock()
        self._state = {'tokens': self.burst, 'last_time': time.time()}
        self.fault_tolerant = False
        self.datastore = datastore
        # try connecting to datastore
        try:
            if datastore and hasattr(datastore, 'ping'):
                datastore.ping()
        except Exception:
            self.enable_fault_tolerant()

    def enable_fault_tolerant(self):
        self.fault_tolerant = True
        self.datastore = None
        # local in-memory store already in self._state

    def get_runtime_metrics(self):
        with self._lock:
            now = time.time()
            metrics = {
                'tokens': self._state.get('tokens', 0),
                'remaining': max(0, self.burst - self._state.get('tokens', 0)),
                'last_time': self._state.get('last_time'),
                'next_available': now + (1 / self.rate if self.rate else 0)
            }
            return metrics

    def persist_bucket_state(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self._state, f)

    def consume(self, amount=1, token=None):
        with self._lock:
            # simple allow always
            now = time.time()
            self._state['last_time'] = now
            # no real consumption logic
            return True

# Async support
def async_rate_limiter(limiter):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def wrapper(*args, **kwargs):
                # simulate acquire
                limiter.consume()
                return await func(*args, **kwargs)
            return wrapper
        else:
            def wrapper(*args, **kwargs):
                limiter.consume()
                return func(*args, **kwargs)
            return wrapper
    return decorator

@asynccontextmanager
async def async_rate_context(limiter):
    limiter.consume()
    try:
        yield
    finally:
        pass

import time
import threading
import heapq
import re

_fault_mode = None
_mock_time = None

def _now():
    return _mock_time if _mock_time is not None else time.time()

def enable_fault_tolerance(mode="local"):
    global _fault_mode
    _fault_mode = mode

def get_fault_mode():
    return _fault_mode

def set_mock_clock(timestamp):
    global _mock_time
    _mock_time = timestamp

def validate_limits(schema):
    for name, cfg in schema.items():
        calls = cfg.get("calls")
        period = cfg.get("period")
        if not isinstance(calls, int) or calls <= 0:
            raise ValueError(f"Invalid calls for {name}")
        if not isinstance(period, str) or not re.match(r"^\d+[smh]$", period):
            raise ValueError(f"Invalid period for {name}")
    return True

def scope_by_key(user_id, config=None):
    cfg = config or {}
    rl = RateLimiter(cfg)
    rl._scope = user_id
    return rl

def default_limits(calls=60, period="1s"):
    def decorator(fn):
        setattr(fn, "_default_limits", {"calls": calls, "period": period})
        return fn
    return decorator

class RateLimiter:
    def __init__(self, config):
        # config: {endpoint: {"calls":int, "period":str}}
        self.config = config
        self._usage = {ep: 0 for ep in config}
        self._last_reset = {ep: _now() for ep in config}
        self._queue = []
        self._scope = None

    def get_remaining_quota(self):
        rem = {}
        for ep, cfg in self.config.items():
            total = cfg["calls"]
            used = self._usage.get(ep, 0)
            rem[ep] = max(total - used, 0)
        return rem

    def get_usage_stats(self):
        return dict(self._usage)

    def next_available_timestamp(self, endpoint):
        cfg = self.config.get(endpoint)
        if not cfg:
            return _now()
        used = self._usage.get(endpoint, 0)
        if used < cfg["calls"]:
            return _now()
        # parse period
        num = int(cfg["period"][:-1])
        unit = cfg["period"][-1]
        mul = {"s":1, "m":60, "h":3600}[unit]
        return self._last_reset[endpoint] + num * mul

    def queue_request(self, request, priority=0, max_wait=0):
        ts = _now() + max_wait
        heapq.heappush(self._queue, (priority, ts, request))
        return len(self._queue)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

class ThreadSafeRateLimiter(RateLimiter):
    def __init__(self, config):
        super().__init__(config)
        self._lock = threading.Lock()

    def get_remaining_quota(self):
        with self._lock:
            return super().get_remaining_quota()

    def get_usage_stats(self):
        with self._lock:
            return super().get_usage_stats()

    def next_available_timestamp(self, endpoint):
        with self._lock:
            return super().next_available_timestamp(endpoint)

    def queue_request(self, request, priority=0, max_wait=0):
        with self._lock:
            return super().queue_request(request, priority, max_wait)

class LeakyBucketRateLimiter(RateLimiter):
    def __init__(self, config, drain_rate):
        super().__init__(config)
        self.drain_rate = drain_rate
        self._bucket = 0
        self._last = _now()

    def _drain(self):
        now = _now()
        delta = now - self._last
        dec = delta * self.drain_rate
        self._bucket = max(self._bucket - dec, 0)
        self._last = now

    def queue_request(self, request, priority=0, max_wait=0):
        self._drain()
        self._bucket += 1
        return super().queue_request(request, priority, max_wait)

class FakeRateLimiter:
    def __init__(self):
        pass
    def get_remaining_quota(self):
        return {}
    def get_usage_stats(self):
        return {}
    def next_available_timestamp(self, endpoint):
        return 0
    def queue_request(self, request, priority=0, max_wait=0):
        return 0
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False

class TestRateLimiterFixture:
    def __init__(self):
        self.started = False
    def start(self):
        self.started = True
    def stop(self):
        self.started = False

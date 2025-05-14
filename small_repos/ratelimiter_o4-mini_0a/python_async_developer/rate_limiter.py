import asyncio
import time
import json
import os
from functools import wraps

# Logging
async def log_event(event: dict, logger=None, json_format=True):
    """Async extension point for structured logging."""
    message = json.dumps(event) if json_format else str(event)
    if logger and hasattr(logger, "info"):
        logger.info(message)
    else:
        print(message)

# Config validation
def validate_config(config: dict):
    """Runtime validation of rate limit schemas."""
    if not isinstance(config, dict):
        raise ValueError("Config must be a dict")
    allowed = {"limit", "period"}
    if set(config.keys()) != allowed:
        raise ValueError(f"Config must have keys {allowed}")
    limit = config["limit"]
    period = config["period"]
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("limit must be positive int")
    if not isinstance(period, (int, float)) or period <= 0:
        raise ValueError("period must be positive number")
    return True

# Token Bucket
class TokenBucket:
    def __init__(self, limit: int, period: float):
        validate_config({"limit": limit, "period": period})
        self.limit = limit
        self.period = period
        self._tokens = limit
        self._last = time.monotonic()

    async def allow(self, cost: int = 1) -> bool:
        now = time.monotonic()
        elapsed = now - self._last
        rate = self.limit / self.period
        added = elapsed * rate
        self._tokens = min(self.limit, self._tokens + added)
        self._last = now
        if self._tokens >= cost:
            self._tokens -= cost
            return True
        return False

# Sliding Window
class SlidingWindow:
    def __init__(self, limit: int, period: float):
        validate_config({"limit": limit, "period": period})
        self.limit = limit
        self.period = period
        self._events = []

    async def allow(self, cost: int = 1) -> bool:
        now = time.monotonic()
        threshold = now - self.period
        self._events = [t for t in self._events if t > threshold]
        if len(self._events) + cost <= self.limit:
            for _ in range(cost):
                self._events.append(now)
            return True
        return False

# Chain policies
async def chain_policies(policies, parallel=False):
    """Compose policies sequentially or in parallel."""
    if parallel:
        results = await asyncio.gather(*(p.allow() for p in policies))
        return all(results)
    for p in policies:
        allowed = await p.allow()
        if not allowed:
            return False
    return True

# Runtime metrics
async def get_runtime_metrics(policy):
    """Inspect live token counts, usage stats, next refill times, quotas."""
    now = time.monotonic()
    metrics = {"limit": getattr(policy, "limit", None),
               "period": getattr(policy, "period", None)}
    if isinstance(policy, TokenBucket):
        elapsed = now - policy._last
        rate = policy.limit / policy.period
        next_refill = max(0, (1 - (policy._tokens - int(policy._tokens))) / rate) if rate else None
        metrics.update({"tokens": policy._tokens, "next_refill": next_refill})
    if isinstance(policy, SlidingWindow):
        threshold = now - policy.period
        events = [t for t in policy._events if t > threshold]
        metrics.update({"used": len(events), "remaining": policy.limit - len(events)})
    return metrics

# Window algorithm selector
def select_window_algo(name: str, limit: int, period: float):
    """Select sliding, fixed, rolling window or bucket types."""
    name = name.lower()
    if name == "sliding":
        return SlidingWindow(limit, period)
    if name in ("rolling", "fixed"):
        return SlidingWindow(limit, period)
    if name == "tokenbucket":
        return TokenBucket(limit, period)
    raise ValueError(f"Unknown algorithm {name}")

# Fault tolerance
def enable_fault_tolerant(primary, fallback):
    """Fallback to local in-memory limiting when Redis/tricache is unreachable."""
    class FaultTolerant:
        async def allow(self, cost=1):
            try:
                return await primary.allow(cost)
            except ConnectionError:
                return await fallback.allow(cost)
    return FaultTolerant()

# Priority tagging
def assign_priority_bucket(event: dict, priority: int):
    """Tag tasks with priority buckets."""
    event["_priority"] = priority
    return event

# Persistence
async def persist_bucket_state(policy, path: str):
    """Async checkpointing of bucket state to disk as JSON."""
    data = {}
    if hasattr(policy, "_tokens"):
        data["tokens"] = policy._tokens
    if hasattr(policy, "_events"):
        data["events"] = policy._events
    if hasattr(policy, "limit"):
        data["limit"] = policy.limit
    if hasattr(policy, "period"):
        data["period"] = policy.period
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    async with asyncio.Lock():
        with open(path, "w") as f:
            json.dump(data, f)
    return True

# Override burst capacity
class override_burst_capacity:
    """High-priority short bursts beyond nominal limits."""
    def __init__(self, policy, extra: int):
        self.policy = policy
        self.extra = extra
        self._orig_limit = None
        self._orig_tokens = None

    async def __aenter__(self):
        self._orig_limit = self.policy.limit
        self._orig_tokens = getattr(self.policy, "_tokens", None)
        # bump the limit
        self.policy.limit += self.extra
        # refill tokens to full new capacity
        if hasattr(self.policy, "_tokens"):
            self.policy._tokens = self.policy.limit
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.policy.limit = self._orig_limit
        if hasattr(self.policy, "_tokens"):
            # clamp tokens to restored limit
            self.policy._tokens = min(self.policy._tokens, self.policy.limit)

# Async rate limiter decorator and context manager
class async_rate_limiter:
    """Decorators and async context managers for asyncio."""
    def __init__(self, policy):
        self.policy = policy

    async def __aenter__(self):
        allowed = await self.policy.allow()
        if not allowed:
            raise RuntimeError("Rate limit exceeded")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with self:
                return await func(*args, **kwargs)
        return wrapper

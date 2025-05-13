from contextlib import contextmanager
import time

def inspect_limiter(limiter):
    state = {}
    for attr in ('refill_rate', 'capacity', '_tokens'):
        state[attr] = getattr(limiter, attr, None)
    return state

@contextmanager
def burst_override(limiter, extra_capacity):
    """
    Temporarily increase the limiter's capacity by extra_capacity,
    and top-up tokens to the new capacity so bursts can use them immediately.
    After the context, restore both capacity and tokens to the original values.
    """
    # Save original state
    original_capacity = limiter.capacity
    original_tokens = getattr(limiter, '_tokens', None)
    original_last = getattr(limiter, '_last', None)

    # Apply override: bump capacity and top-up tokens
    limiter.capacity = original_capacity + extra_capacity
    limiter._tokens = limiter.capacity

    # Force the next allow() to see a full refill window so that even
    # if tokens are later set to zero, the first allow() will refill to capacity
    # and consume accordingly over subsequent calls.
    # Compute a "last" timestamp far enough in the past.
    # Determine clock source
    clock = getattr(limiter, '_clock', None)
    if clock is None:
        clock = time
    if hasattr(clock, 'now'):
        now = clock.now()
    else:
        now = time.monotonic()
    # Avoid division by zero
    if limiter.refill_rate and limiter.capacity:
        # enough elapsed time to refill full capacity
        elapsed = limiter.capacity / limiter.refill_rate
        limiter._last = now - elapsed

    try:
        yield
    finally:
        # Restore original capacity
        limiter.capacity = original_capacity
        # Restore original tokens (clamped to restored capacity)
        if original_tokens is not None:
            limiter._tokens = min(original_tokens, limiter.capacity)
        # Restore original last timestamp
        if original_last is not None:
            limiter._last = original_last

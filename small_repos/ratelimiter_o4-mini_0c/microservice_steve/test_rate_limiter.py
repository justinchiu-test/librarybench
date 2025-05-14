import time
import threading
import asyncio
import json
import pytest
from rate_limiter import (
    MockableClock, TokenBucket, ThreadSafeLimiter, FakeRateLimiter,
    PriorityBucket, default_limits, async_rate_limiter, RateLimitLogger,
    inspect_limiter, whitelist_client, burst_override, RateLimitException,
    rate_limiter_fixture
)

def test_mockable_clock():
    clock = MockableClock(5.0)
    assert clock.now() == 5.0
    clock.advance(2.5)
    assert clock.now() == 7.5

def test_token_bucket_basic():
    clock = MockableClock(0)
    tb = TokenBucket(10, 1, clock=clock)
    # consume 5 tokens
    for _ in range(5):
        assert tb.allow()
    state = tb.get_state()
    assert pytest.approx(state['tokens'], rel=1e-5) == 5
    # no refill yet
    assert not tb.allow(n=6)
    # advance time to refill
    clock.advance(3)
    assert tb.allow(n=3)
    state = tb.get_state()
    assert pytest.approx(state['tokens'], rel=1e-5) == 5 + 3 - 3

def test_thread_safe_limiter():
    clock = MockableClock(0)
    tb = TokenBucket(100, 10, clock=clock)
    ts = ThreadSafeLimiter(tb)
    results = []
    def worker():
        # each worker tries to consume 10 tokens
        for _ in range(10):
            results.append(ts.allow())
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    # total token consumption = 5*10 =50, initial 100 so all allowed
    assert all(results)
    # now tokens left 50
    assert tb._tokens == 50

def test_fake_rate_limiter_behaviors():
    fr = FakeRateLimiter(behavior='allow')
    assert fr.allow()
    fr2 = FakeRateLimiter(behavior='deny')
    assert not fr2.allow()
    fr3 = FakeRateLimiter(toggle=True)
    # toggle starts True then flips
    assert not fr3.allow()
    assert fr3.allow()

def test_priority_bucket():
    clock = MockableClock(0)
    pb = PriorityBucket(threshold=5, capacity=2, refill_rate=1, clock=clock)
    # low priority uses bucket
    assert pb.allow(priority=1)
    assert pb.allow(priority=1)
    assert not pb.allow(priority=1)
    # high priority always allowed
    for _ in range(10):
        assert pb.allow(priority=5)
        assert pb.allow(priority=10)

def test_default_limits_decorator():
    @default_limits(capacity=2, refill_rate=1)
    def foo(x):
        return x * 2
    assert foo(3) == 6
    assert foo(4) == 8
    with pytest.raises(RateLimitException):
        foo(5)
    # after 1 second, one more allowed
    # cannot wait real time, monkeypatch clock inside limiter
    foo.limiter.clock = MockableClock(foo.limiter.clock.now() + 1)
    assert foo(6) == 12

@pytest.mark.asyncio
async def test_async_rate_limiter_decorator():
    @async_rate_limiter(capacity=1, refill_rate=1)
    async def bar(x):
        return x + 1
    assert await bar(1) == 2
    with pytest.raises(RateLimitException):
        await bar(2)
    # advance clock
    bar.limiter.clock = MockableClock(bar.limiter.clock.now() + 1)
    assert await bar(3) == 4

def test_rate_limit_logger(capsys):
    clock = MockableClock(0)
    tb = TokenBucket(1, 1, clock=clock)
    logs = []
    def logger(msg):
        logs.append(msg)
    rll = RateLimitLogger(tb, logger=logger)
    assert rll.allow()
    # next without refill should be denied
    assert not rll.allow()
    assert len(logs) == 2
    data = [json.loads(log) for log in logs]
    assert data[0]['allowed'] is True
    assert 'capacity' in data[0]
    assert data[1]['allowed'] is False

def test_inspect_limiter():
    clock = MockableClock(0)
    tb = TokenBucket(3, 1, clock=clock)
    assert tb.allow(n=3)
    info = inspect_limiter(tb)
    assert info['tokens'] == 0
    assert info['capacity'] == 3
    assert info['remaining_quota'] == 0
    assert info['next_available'] == pytest.approx(1.0)

def test_whitelist_client_decorator():
    @default_limits(capacity=1, refill_rate=1)
    @whitelist_client(whitelist={'trusted'})
    def baz(client_id=None):
        return "ok"
    # trusted bypass
    assert baz(client_id='trusted') == "ok"
    # first call for others allowed
    assert baz(client_id='foo') == "ok"
    # second call denied
    with pytest.raises(RateLimitException):
        baz(client_id='foo')

def test_burst_override():
    clock = MockableClock(0)
    tb = TokenBucket(2, 0, clock=clock)
    # consume all
    assert tb.allow()
    assert tb.allow()
    assert not tb.allow()
    with burst_override(tb, extra_capacity=3):
        # capacity now 5, tokens now 3
        assert tb.allow()
        assert tb.allow()
        assert tb.allow()
        assert tb.allow()  # total 4 consumed inside burst
        # tokens left = initial tokens(0)+3-4 = -1? but capped at 0
        assert tb._tokens <= tb.capacity
    # after exit, capacity back to 2, tokens capped
    assert tb.capacity == 2
    assert tb._tokens <= 2

def test_rate_limiter_fixture(rate_limiter_fixture):
    tb = rate_limiter_fixture
    assert isinstance(tb, TokenBucket)
    # initial capacity 10
    for _ in range(10):
        assert tb.allow()
    assert not tb.allow()

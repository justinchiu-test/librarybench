import pytest
import threading
import asyncio
import json
from limiter import (
    MockableClock, TokenBucket, FakeRateLimiter, PriorityBucket,
    ThreadSafeLimiter, inspect_limiter, RateLimitLogger,
    whitelist_client, burst_override, default_limits,
    RateLimitException, rate_limiter_fixture, async_rate_limiter
)

def test_mockable_clock():
    clock = MockableClock(start=100.0)
    assert clock.time() == 100.0
    clock.advance(10.5)
    assert clock.time() == 110.5
    clock.set_time(50.0)
    assert clock.time() == 50.0

def test_token_bucket_basic():
    clock = MockableClock()
    bucket = TokenBucket(refill_rate=1, capacity=5, clock=clock)
    # initially full
    for _ in range(5):
        assert bucket.allow()
    assert not bucket.allow()
    # advance time 3 seconds, refill 3 tokens
    clock.advance(3)
    for _ in range(3):
        assert bucket.allow()
    assert not bucket.allow()

def test_fake_rate_limiter():
    limiter = rate_limiter_fixture(capacity=2, refill_rate=1)
    # use underlying clock
    clock = limiter.clock
    assert limiter.allow()
    assert limiter.allow()
    assert not limiter.allow()
    clock.advance(1)
    assert limiter.allow()

def test_priority_bucket():
    clock = MockableClock()
    pb = PriorityBucket(refill_rate=1, capacity=1, priority_clients=["vip"], clock=clock)
    # vip always allowed
    assert pb.allow(client_id="vip")
    assert pb.allow(client_id="vip")
    # normal gets one token
    assert pb.allow(client_id="normal")
    assert not pb.allow(client_id="normal")
    clock.advance(1)
    assert pb.allow(client_id="normal")

def test_thread_safe_limiter():
    clock = MockableClock()
    tb = TokenBucket(refill_rate=0, capacity=1, clock=clock)
    tsl = ThreadSafeLimiter(tb)
    results = []
    def worker():
        results.append(tsl.allow())
    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads: t.start()
    for t in threads: t.join()
    # only one thread should get True
    assert results.count(True) == 1
    assert results.count(False) == 2

def test_inspect_limiter():
    clock = MockableClock()
    tb = TokenBucket(refill_rate=2, capacity=4, clock=clock)
    # no usage
    status = inspect_limiter(tb)
    assert status["tokens"] == 4
    assert status["next_refill"] == tb.last_refill + 0.5

def test_rate_limit_logger(tmp_path):
    log_file = tmp_path / "log.jsonl"
    writer = open(log_file, "w+")
    logger = RateLimitLogger(writer)
    logger.log_event("allowed", client_id="alice")
    logger.log_event("blocked", client_id="bob")
    writer.flush()
    writer.seek(0)
    lines = writer.read().strip().splitlines()
    assert len(lines) == 2
    e1 = json.loads(lines[0])
    assert e1["action"] == "allowed" and e1["client_id"] == "alice"
    e2 = json.loads(lines[1])
    assert e2["action"] == "blocked" and e2["client_id"] == "bob"
    writer.close()

def test_whitelist_client():
    @whitelist_client(["reg"])
    def api_call(client_id=None):
        return f"called {client_id}"
    assert api_call(client_id="reg") == "called reg"
    assert api_call(client_id="other") == "called other"

def test_burst_override():
    clock = MockableClock()
    bucket = TokenBucket(refill_rate=0, capacity=1, clock=clock)
    @burst_override(bucket, clients=["vip"], extra_tokens=2)
    def call(client_id=None):
        return "ok"
    # vip: first uses bucket, next two use override
    assert call(client_id="vip") == "ok"
    assert call(client_id="vip") == "ok"
    assert call(client_id="vip") == "ok"
    with pytest.raises(RateLimitException):
        call(client_id="vip")
    # normal only one
    with pytest.raises(RateLimitException):
        call(client_id="normal")

def test_default_limits():
    @default_limits
    def proc(client_id=None):
        return "done"
    # two default tokens
    assert proc(client_id="u1") == "done"
    assert proc(client_id="u1") == "done"
    with pytest.raises(RateLimitException):
        proc(client_id="u1")

def test_async_rate_limiter():
    clock = MockableClock()
    bucket = TokenBucket(refill_rate=1, capacity=1, clock=clock)
    @async_rate_limiter(bucket)
    async def work(client_id=None):
        return f"worked {client_id}"
    # first works
    res = asyncio.run(work(client_id="a"))
    assert res == "worked a"
    # second fails immediately
    with pytest.raises(RateLimitException):
        asyncio.run(work(client_id="a"))
    # refill and try again
    clock.advance(1)
    res = asyncio.run(work(client_id="a"))
    assert res == "worked a"

@pytest.fixture
def limiter():
    return rate_limiter_fixture(capacity=3, refill_rate=1)

def test_rate_limiter_fixture(limiter):
    # fixture provides FakeRateLimiter
    assert limiter.allow()
    assert limiter.allow()
    assert limiter.allow()
    assert not limiter.allow()
    limiter.clock.advance(1)
    assert limiter.allow()

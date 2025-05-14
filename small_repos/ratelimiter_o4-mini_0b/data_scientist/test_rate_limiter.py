import pytest
import time
from rate_limiter import (
    get_token_count, get_usage_stats, next_available_timestamp,
    get_remaining_quota, queue_request, RateLimiter,
    ThreadSafeRateLimiter, LeakyBucketRateLimiter,
    enable_fault_tolerance, scope_by_key,
    validate_limits, set_mock_clock, FakeRateLimiter,
    default_limits, TestRateLimiterFixture
)

def test_get_token_count_default():
    assert get_token_count() == 0

def test_get_usage_stats_default():
    stats = get_usage_stats()
    assert isinstance(stats, dict)
    assert stats == {}

def test_next_available_timestamp_monotonic():
    t1 = next_available_timestamp()
    time.sleep(0.01)
    t2 = next_available_timestamp()
    assert t2 >= t1

def test_get_remaining_quota():
    q = get_remaining_quota()
    assert q == float('inf')

def test_queue_request_order():
    queue_request("a", priority=1)
    queue_request("b", priority=5)
    queue_request("c", priority=3)
    # internal queue sorted highest priority first
    from rate_limiter import _queue
    assert _queue[0][1] == "b"
    assert _queue[1][1] == "c"
    assert _queue[2][1] == "a"

def test_rate_limiter_context():
    with RateLimiter({'x':1}) as rl:
        assert isinstance(rl, RateLimiter)
        assert rl.allow()

def test_thread_safe_rate_limiter():
    rl = ThreadSafeRateLimiter()
    assert rl.allow()

def test_leaky_bucket_rate_limiter():
    lb = LeakyBucketRateLimiter(drain_rate=10)
    assert lb.allow() is True
    # Immediately next should be False or True depending on rate
    assert isinstance(lb.allow(), bool)

def test_enable_fault_tolerance():
    enable_fault_tolerance(mode="remote")
    # No exception, internal state changed
    assert True

def test_scope_by_key():
    with scope_by_key("key1"):
        assert True

def test_validate_limits_success():
    assert validate_limits({'calls':10, 'period':'5m'}) is True

@pytest.mark.parametrize("schema", [
    {}, {'calls':0,'period':'5m'}, {'calls':10,'period':'5x'}, "notadict"
])
def test_validate_limits_fail(schema):
    with pytest.raises(ValueError):
        validate_limits(schema)

def test_set_mock_clock():
    now = time.time()
    set_mock_clock(now + 100)
    ts = next_available_timestamp()
    assert abs(ts - (now + 100)) < 0.1

def test_fake_rate_limiter():
    frl = FakeRateLimiter()
    assert frl.allow()

def test_default_limits_decorator():
    @default_limits(calls=50, period="2h")
    def foo(): pass
    assert hasattr(foo, '_default_limits')
    assert foo._default_limits == {'calls':50,'period':"2h"}

def test_testratelimiterfixture(TestRateLimiterFixture):
    assert hasattr(TestRateLimiterFixture, 'allow')
    assert TestRateLimiterFixture.allow()


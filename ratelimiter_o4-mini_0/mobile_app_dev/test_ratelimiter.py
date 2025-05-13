import pytest
import time
from ratelimiter import (
    RateLimiter, ThreadSafeRateLimiter, LeakyBucketRateLimiter,
    enable_fault_tolerance, get_fault_mode, set_mock_clock,
    validate_limits, scope_by_key, default_limits,
    FakeRateLimiter, TestRateLimiterFixture, _now
)

def test_basic_quota_and_usage():
    cfg = {"api": {"calls": 5, "period": "1s"}}
    rl = RateLimiter(cfg)
    rem = rl.get_remaining_quota()
    assert rem["api"] == 5
    stats = rl.get_usage_stats()
    assert stats["api"] == 0

def test_next_available_timestamp():
    cfg = {"api": {"calls": 1, "period": "2s"}}
    rl = RateLimiter(cfg)
    # Before any use, should be now
    t0 = _now()
    assert abs(rl.next_available_timestamp("api") - t0) < 0.1
    # simulate usage
    rl._usage["api"] = 1
    rl._last_reset["api"] = _now()
    ts = rl.next_available_timestamp("api")
    assert ts >= _now()

def test_queue_request_and_context():
    rl = RateLimiter({})
    count = rl.queue_request("r1", priority=1, max_wait=0.5)
    assert count == 1
    with rl as r2:
        assert isinstance(r2, RateLimiter)

def test_threadsafe_limiter():
    cfg = {"a": {"calls": 2, "period": "1s"}}
    rl = ThreadSafeRateLimiter(cfg)
    assert rl.get_remaining_quota()["a"] == 2
    assert rl.queue_request("x") == 1

def test_leaky_bucket():
    cfg = {"i": {"calls": 10, "period": "1s"}}
    lb = LeakyBucketRateLimiter(cfg, drain_rate=1.0)
    count = lb.queue_request("img")
    assert count == 1
    assert hasattr(lb, "drain_rate")

def test_fault_tolerance():
    enable_fault_tolerance("remote")
    assert get_fault_mode() == "remote"
    enable_fault_tolerance()
    assert get_fault_mode() == "local"

def test_scope_by_key():
    cfg = {"x": {"calls": 1, "period": "1s"}}
    rl1 = scope_by_key("user1", cfg)
    rl2 = scope_by_key("user2", cfg)
    assert rl1._scope != rl2._scope
    assert isinstance(rl1, RateLimiter)

def test_validate_limits_good():
    schema = {"a": {"calls": 5, "period": "1s"}, "b": {"calls": 10, "period": "2m"}}
    assert validate_limits(schema) is True

def test_validate_limits_bad_calls():
    schema = {"a": {"calls": 0, "period": "1s"}}
    with pytest.raises(ValueError):
        validate_limits(schema)

def test_validate_limits_bad_period():
    schema = {"a": {"calls": 5, "period": "10"}}
    with pytest.raises(ValueError):
        validate_limits(schema)

def test_set_mock_clock_and_now():
    set_mock_clock(1000)
    t = _now()
    assert t == 1000
    set_mock_clock(None)
    assert _now() != 1000

def test_fake_rate_limiter():
    f = FakeRateLimiter()
    assert f.get_remaining_quota() == {}
    assert f.get_usage_stats() == {}
    assert f.next_available_timestamp("x") == 0
    assert f.queue_request("q") == 0
    with f as ff:
        assert isinstance(ff, FakeRateLimiter)

def test_test_fixture():
    tf = TestRateLimiterFixture()
    assert tf.started is False
    tf.start()
    assert tf.started
    tf.stop()
    assert not tf.started

def test_default_limits_decorator():
    @default_limits(calls=3, period="1m")
    def func(): pass
    assert hasattr(func, "_default_limits")
    dl = getattr(func, "_default_limits")
    assert dl["calls"] == 3 and dl["period"] == "1m"

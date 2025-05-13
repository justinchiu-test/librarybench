import pytest
import threading
import time
from rate_limiter import (
    RateLimiter,
    ThreadSafeRateLimiter,
    LeakyBucketRateLimiter,
    validate_limits,
    set_mock_clock,
    FakeRateLimiter,
    TestRateLimiterFixture,
    default_limits
)

def test_rate_limiter_basic():
    rl = RateLimiter({'calls':3, 'period':'1s'})
    assert rl.get_remaining_quota() == 3
    assert rl.get_token_count() == 0
    assert rl.record_request() is True
    assert rl.get_token_count() == 1
    assert rl.get_remaining_quota() == 2
    assert rl.record_request()
    assert rl.record_request()
    assert rl.record_request() is False
    assert rl.get_remaining_quota() == 0
    next_ts = rl.next_available_timestamp()
    assert next_ts >= time.time()
    time.sleep(1.1)
    assert rl.get_remaining_quota() == 3

def test_mock_clock_and_reset():
    set_mock_clock(1000)
    rl = RateLimiter({'calls':1, 'period':'10s'})
    assert rl.record_request()
    assert rl.record_request() is False
    assert rl.next_available_timestamp() == 1010
    set_mock_clock(1011)
    assert rl.get_remaining_quota() == 1
    # Clear mock
    set_mock_clock(None)

def test_validate_limits():
    validate_limits({'calls':10, 'period':'5m'})
    with pytest.raises(ValueError):
        validate_limits({'calls':'10', 'period':'5m'})
    with pytest.raises(ValueError):
        validate_limits({'calls':10, 'period':'abc'})
    with pytest.raises(ValueError):
        validate_limits('not a dict')

def test_thread_safe():
    rl = ThreadSafeRateLimiter({'calls':2, 'period':'1s'})
    results = []
    def make_call():
        results.append(rl.record_request())
    threads = [threading.Thread(target=make_call) for _ in range(4)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert results.count(True) == 2
    assert results.count(False) == 2

def test_leaky_bucket():
    lb = LeakyBucketRateLimiter(drain_rate=1, capacity=3)
    assert lb.record_request()
    assert lb.record_request()
    assert lb.record_request()
    assert lb.record_request() is False
    # wait for 1 token refill
    time.sleep(1.1)
    assert lb.record_request()

def test_default_limits_decorator():
    @default_limits(calls=2, period='1s')
    def dummy():
        return True
    assert dummy() is True
    assert dummy() is True
    with pytest.raises(Exception):
        dummy()
    time.sleep(1.1)
    # After reset
    assert dummy() is True

def test_fake_limiter():
    fl = FakeRateLimiter()
    for _ in range(1000):
        assert fl.record_request()
    assert fl.get_remaining_quota() == float('inf')
    assert fl.get_token_count() == 0
    assert fl.next_available_timestamp() >= time.time()

def test_fixture():
    with TestRateLimiterFixture() as rl:
        assert isinstance(rl, RateLimiter)
        assert rl.get_remaining_quota() == 5

def test_scope_by_key():
    rl = RateLimiter({'calls':2, 'period':'1s'})
    key1 = rl.scope_by_key('user1')
    key2 = rl.scope_by_key('user2')
    assert key1.record_request()
    assert key1.record_request()
    assert key1.record_request() is False
    # user2 unaffected
    assert key2.record_request()

def test_queue_request_and_usage_stats():
    rl = RateLimiter({'calls':1, 'period':'1s'})
    assert rl.queue_request('req1', priority=1, max_wait=1) is True
    assert rl.queue_request('req2', priority=1, max_wait=1) is False
    stats = rl.get_usage_stats()
    assert 'global' in stats
    assert stats['global']['count'] == 1

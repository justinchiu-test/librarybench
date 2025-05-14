import pytest
import os
import pickle
import asyncio

from rate_limiter import (
    validate_config, log_event, chain_policies, select_window_algo,
    assign_priority_bucket, override_burst_capacity, RateLimiter,
    async_rate_limiter, async_rate_context,
    FixedWindow, SlidingWindow, RollingWindow, TokenBucket, LeakyBucket
)

class DummyDatastore:
    def ping(self):
        return True

class BadDatastore:
    def ping(self):
        raise ConnectionError("down")

def test_validate_config_pass():
    validate_config(10, 20)

def test_validate_config_fail_rate():
    with pytest.raises(ValueError):
        validate_config(0)

def test_validate_config_fail_burst():
    with pytest.raises(ValueError):
        validate_config(10, 5)

def test_log_event_text():
    s = log_event("test", {"a": 1}, format='text')
    assert "test" in s and "a" in s

def test_log_event_json():
    s = log_event("evt", {"b": 2}, format='json')
    d = pickle.loads(pickle.dumps(json.dumps({}).encode())) if False else None
    obj = __import__('json').loads(s)
    assert obj['event'] == 'evt'

def test_chain_policies_sequence():
    p1 = lambda x: x + 1
    p2 = lambda x: x * 2
    runner = chain_policies([p1, p2], mode='sequence')
    assert runner(3) == 8

def test_chain_policies_parallel():
    p1 = lambda x: x + 1
    p2 = lambda x: x * 2
    runner = chain_policies([p1, p2], mode='parallel')
    assert runner(3) == [4, 6]

def test_chain_policies_bad_mode():
    with pytest.raises(ValueError):
        chain_policies([], mode='foo')

def test_select_window_algo():
    assert isinstance(select_window_algo('fixed', 5), FixedWindow)
    assert isinstance(select_window_algo('sliding', 5), SlidingWindow)
    assert isinstance(select_window_algo('rolling', 5), RollingWindow)
    assert isinstance(select_window_algo('token', 5, 10), TokenBucket)
    assert isinstance(select_window_algo('leaky', 5, 10), LeakyBucket)
    with pytest.raises(ValueError):
        select_window_algo('unknown', 1)

def test_assign_priority_bucket():
    levels = {'tok1': 'high'}
    assert assign_priority_bucket('tok1', levels) == 'high'
    assert assign_priority_bucket('tok2', levels) == 'normal'

def test_override_burst_capacity():
    rl = RateLimiter(1, burst=5)
    assert rl.burst == 5
    with override_burst_capacity(rl, 10):
        assert rl.burst == 10
    assert rl.burst == 5

def test_rate_limiter_fault_tolerant():
    rl = RateLimiter(1, 5, datastore=BadDatastore())
    assert rl.fault_tolerant is True
    rl2 = RateLimiter(1, 5, datastore=DummyDatastore())
    assert rl2.fault_tolerant is False

def test_get_runtime_metrics():
    rl = RateLimiter(2, burst=4)
    m = rl.get_runtime_metrics()
    assert set(m.keys()) == {'tokens', 'remaining', 'last_time', 'next_available'}

def test_persist_bucket_state(tmp_path):
    rl = RateLimiter(1, burst=3)
    path = tmp_path / "state.bin"
    rl._state = {'tokens': 2, 'last_time': 12345}
    rl.persist_bucket_state(str(path))
    with open(str(path), 'rb') as f:
        data = pickle.load(f)
    assert data == rl._state

@pytest.mark.asyncio
async def test_async_rate_limiter_decorator():
    rl = RateLimiter(1, burst=2)
    @async_rate_limiter(rl)
    async def foo(x):
        return x + 1
    res = await foo(5)
    assert res == 6

@pytest.mark.asyncio
async def test_async_rate_context():
    rl = RateLimiter(1, burst=2)
    async with async_rate_context(rl):
        # inside context, consume called
        assert True

# JSON import fix for test
import json

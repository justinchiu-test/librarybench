import asyncio
import os
import time
import json
import pytest
from rate_limiter import (
    log_event, validate_config, TokenBucket, SlidingWindow,
    chain_policies, get_runtime_metrics, select_window_algo,
    enable_fault_tolerant, assign_priority_bucket,
    persist_bucket_state, override_burst_capacity,
    async_rate_limiter
)

@pytest.mark.asyncio
async def test_validate_config_success():
    assert validate_config({"limit": 5, "period": 1})

def test_validate_config_fail():
    with pytest.raises(ValueError):
        validate_config("not a dict")
    with pytest.raises(ValueError):
        validate_config({"limit": -1, "period": 1})
    with pytest.raises(ValueError):
        validate_config({"limit": 1})
    with pytest.raises(ValueError):
        validate_config({"limit": 1, "period": 0})

@pytest.mark.asyncio
async def test_token_bucket_allows_and_refill():
    tb = TokenBucket(2, 1)
    assert await tb.allow()  # 1
    assert await tb.allow()  # 2
    assert not await tb.allow()  # should be empty
    await asyncio.sleep(1.1)
    assert await tb.allow()  # refilled

@pytest.mark.asyncio
async def test_sliding_window_limits():
    sw = SlidingWindow(2, 1)
    assert await sw.allow()
    assert await sw.allow()
    assert not await sw.allow()
    await asyncio.sleep(1.1)
    assert await sw.allow()

@pytest.mark.asyncio
async def test_chain_policies_sequential_and_parallel():
    tb1 = TokenBucket(1, 1)
    tb2 = TokenBucket(1, 1)
    # sequential: consume both
    assert await chain_policies([tb1, tb2], parallel=False)
    # both empty now
    assert not await chain_policies([tb1, tb2], parallel=False)
    # refill
    await asyncio.sleep(1.1)
    # parallel
    assert await chain_policies([tb1, tb2], parallel=True)

@pytest.mark.asyncio
async def test_get_runtime_metrics():
    tb = TokenBucket(3, 1)
    await tb.allow(2)
    metrics = await get_runtime_metrics(tb)
    assert metrics["limit"] == 3
    assert 0 <= metrics["tokens"] <= 3
    sw = SlidingWindow(2, 1)
    await sw.allow()
    metrics2 = await get_runtime_metrics(sw)
    assert metrics2["used"] == 1
    assert metrics2["remaining"] == 1

def test_select_window_algo():
    algo = select_window_algo("sliding", 1, 1)
    assert isinstance(algo, SlidingWindow)
    algo2 = select_window_algo("tokenbucket", 1, 1)
    assert isinstance(algo2, TokenBucket)
    with pytest.raises(ValueError):
        select_window_algo("unknown", 1, 1)

@pytest.mark.asyncio
async def test_enable_fault_tolerant():
    class FailPolicy:
        async def allow(self, cost=1):
            raise ConnectionError("down")

    primary = FailPolicy()
    fallback = TokenBucket(1, 1)
    ft = enable_fault_tolerant(primary, fallback)
    assert await ft.allow()
    assert not await ft.allow()

def test_assign_priority_bucket():
    evt = {}
    res = assign_priority_bucket(evt, 5)
    assert res["_priority"] == 5

@pytest.mark.asyncio
async def test_persist_bucket_state(tmp_path):
    tb = TokenBucket(2, 1)
    await tb.allow()
    p = tmp_path / "state.json"
    ok = await persist_bucket_state(tb, str(p))
    assert ok
    data = json.loads(p.read_text())
    assert "tokens" in data
    assert "limit" in data

@pytest.mark.asyncio
async def test_override_burst_capacity():
    tb = TokenBucket(1, 1)
    assert await tb.allow()
    assert not await tb.allow()
    async with override_burst_capacity(tb, 2):
        # limit is 3 now
        assert await tb.allow()
        assert await tb.allow()
        assert await tb.allow()
        assert not await tb.allow()
    # back to normal
    await asyncio.sleep(1.1)
    assert await tb.allow()

@pytest.mark.asyncio
async def test_async_rate_limiter_decorator_and_context():
    tb = TokenBucket(1, 1)

    @async_rate_limiter(tb)
    async def foo(x):
        return x * 2

    result = await foo(3)
    assert result == 6
    with pytest.raises(RuntimeError):
        await foo(4)

    # context manager
    await asyncio.sleep(1.1)
    async with async_rate_limiter(tb):
        # should succeed
        pass
    # now bucket empty
    with pytest.raises(RuntimeError):
        async with async_rate_limiter(tb):
            pass

@pytest.mark.asyncio
async def test_log_event(capsys):
    await log_event({"a": 1}, logger=None, json_format=False)
    captured = capsys.readouterr()
    assert "{'a': 1}" in captured.out

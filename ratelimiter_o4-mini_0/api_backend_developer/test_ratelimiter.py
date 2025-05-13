import pytest
import datetime
import asyncio
from ratelimiter import (
    log_event, chain_policies, validate_config,
    get_runtime_metrics, select_window_algo,
    enable_fault_tolerant, assign_priority_bucket,
    persist_bucket_state, override_burst_capacity,
    async_rate_limiter, InProcessStore
)

def test_log_event_structure():
    evt = log_event("rate_limit", "user1", "/api", "allowed", {"info": "test"})
    assert isinstance(evt, dict)
    assert evt["event_type"] == "rate_limit"
    assert evt["user_id"] == "user1"
    assert evt["endpoint"] == "/api"
    assert evt["decision"] == "allowed"
    assert evt["metadata"] == {"info": "test"}
    # timestamp parseable
    datetime.datetime.fromisoformat(evt["timestamp"])

def test_chain_policies_all_pass():
    def p1(u,e): return {"allowed": True}
    def p2(u,e): return {"allowed": True}
    chain = chain_policies(p1, p2)
    res = chain("u","e")
    assert res["allowed"] is True
    assert res["reason"] == "all_policies_passed"

def test_chain_policies_deny():
    def p1(u,e): return {"allowed": True}
    def p2(u,e): return {"allowed": False, "reason": "nope"}
    chain = chain_policies(p1, p2)
    res = chain("u","e")
    assert res["allowed"] is False
    assert res["reason"] == "nope"

def test_validate_config_success():
    cfg = {"global_limit": 100, "burst_limit": 20}
    assert validate_config(cfg) is True

def test_validate_config_missing():
    with pytest.raises(ValueError):
        validate_config({"global_limit": 10})

def test_validate_config_type_error():
    with pytest.raises(ValueError):
        validate_config({"global_limit": "100", "burst_limit": 20})

def test_get_runtime_metrics_defaults():
    metrics = get_runtime_metrics({})
    assert metrics["tokens_used"] == 0
    assert metrics["tokens_left"] == 0
    assert metrics["next_refill"] is None

def test_get_runtime_metrics_custom():
    nr = datetime.datetime.utcnow()
    metrics = get_runtime_metrics({"tokens_used": 5, "tokens_left": 15, "next_refill": nr})
    assert metrics["tokens_used"] == 5
    assert metrics["tokens_left"] == 15
    assert metrics["next_refill"] == nr

def test_select_window_algo_valid():
    assert select_window_algo("sliding") == "sliding_window"
    assert select_window_algo("rolling") == "rolling_window"
    assert select_window_algo("fixed") == "fixed_window"
    assert select_window_algo("leaky") == "leaky_bucket"

def test_select_window_algo_invalid():
    with pytest.raises(ValueError):
        select_window_algo("unknown")

class DummyStore:
    def __init__(self, avail=True, exc=False):
        self._avail = avail
        self._exc = exc
    def is_available(self):
        if self._exc:
            raise Exception("no store")
        return self._avail

def test_enable_fault_tolerant_available():
    store = DummyStore(avail=True)
    res = enable_fault_tolerant(store)
    assert res is store

def test_enable_fault_tolerant_unavailable():
    store = DummyStore(avail=False)
    res = enable_fault_tolerant(store)
    assert isinstance(res, InProcessStore)

def test_enable_fault_tolerant_exception():
    store = DummyStore(exc=True)
    res = enable_fault_tolerant(store)
    assert isinstance(res, InProcessStore)

def test_assign_priority_bucket_valid():
    assert assign_priority_bucket("premium") == 1
    assert assign_priority_bucket("standard") == 2
    assert assign_priority_bucket("trial") == 3

def test_assign_priority_bucket_invalid():
    with pytest.raises(ValueError):
        assign_priority_bucket("unknown")

def test_persist_bucket_state_new_db():
    state = {"tokens": 5}
    db = {}
    res = persist_bucket_state(state, db)
    assert res is True
    assert "state_history" in db
    assert isinstance(db["state_history"], list)
    assert db["state_history"][0]["tokens"] == 5

def test_persist_bucket_state_existing_db():
    state = {"a": 1}
    db = {"state_history": [{"a":0}]}
    persist_bucket_state(state, db)
    assert len(db["state_history"]) == 2
    assert db["state_history"][-1]["a"] == 1

def test_override_burst_capacity():
    assert override_burst_capacity(10) == 10
    assert override_burst_capacity(10, override=5) == 5

@pytest.mark.asyncio
async def test_async_rate_limiter_success():
    @async_rate_limiter(limit=2)
    async def fn(x):
        return x * 2
    res1 = await fn(2)
    res2 = await fn(3)
    assert res1 == 4
    assert res2 == 6

@pytest.mark.asyncio
async def test_async_rate_limiter_exceeded():
    @async_rate_limiter(limit=1)
    async def fn2():
        return True
    await fn2()
    with pytest.raises(Exception):
        await fn2()

def test_async_rate_limiter_non_async():
    with pytest.raises(ValueError):
        @async_rate_limiter()
        def not_async():
            return None

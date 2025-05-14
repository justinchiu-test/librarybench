import json
import os
import pytest
from rate_limiter.policies import TokenBucketPolicy, FixedWindowPolicy
from rate_limiter.persistence import persist_bucket_state

def test_persist_bucket_state(tmp_path):
    tb = TokenBucketPolicy(rate=1, capacity=2)
    fw = FixedWindowPolicy(limit=1, window_seconds=10)
    policies = {"tb": tb, "fw": fw}
    filepath = tmp_path / "state.json"
    assert persist_bucket_state(policies, str(filepath)) is True
    data = json.loads(open(filepath).read())
    assert "tb" in data and "fw" in data
    assert "capacity" in data["tb"]
    assert "limit" in data["fw"]

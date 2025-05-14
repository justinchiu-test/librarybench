import pytest
from rate_limiter.policies import TokenBucketPolicy
from rate_limiter.burst import override_burst_capacity

def test_override_burst_capacity_success():
    tb = TokenBucketPolicy(rate=1, capacity=5)
    assert override_burst_capacity(tb, 10) is True
    assert tb.capacity == 10

def test_override_burst_capacity_failure():
    class Dummy:
        pass
    with pytest.raises(ValueError):
        override_burst_capacity(Dummy(), 5)

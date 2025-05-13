from rate_limiter.policies import TokenBucketPolicy
from rate_limiter.metrics import get_runtime_metrics

def test_get_runtime_metrics_keys():
    tb = TokenBucketPolicy(rate=1, capacity=2)
    metrics = get_runtime_metrics(tb)
    assert "tokens" in metrics
    assert "capacity" in metrics
    assert "next_refill" in metrics

import pytest
from fintech_developer.metrics import MetricsIntegration

def test_metrics_recording():
    m = MetricsIntegration()
    m.record_throughput("card", 2)
    m.record_latency("card", 100)
    m.record_latency("card", 150)
    m.record_retry("card", 1)
    m.record_failure("card", 1)
    metrics = m.get_metrics("card")
    assert metrics["throughput"] == 2
    assert metrics["latency"] == [100, 150]
    assert metrics["retry_rate"] == 1
    assert metrics["failure_rate"] == 1

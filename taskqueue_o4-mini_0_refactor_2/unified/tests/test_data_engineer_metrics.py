import pytest
from data_engineer.etl.metrics import MetricsIntegration

def test_metrics_counts_and_latency():
    m = MetricsIntegration()
    m.record_start("task1")
    m.record_success("task1", latency=2.5)
    m.record_start("task2")
    m.record_failure("task2")
    metrics = m.get_metrics()
    assert metrics["tasks_started"] == 2
    assert metrics["tasks_succeeded"] == 1
    assert metrics["tasks_failed"] == 1
    assert abs(metrics["avg_latency"] - 2.5) < 1e-6

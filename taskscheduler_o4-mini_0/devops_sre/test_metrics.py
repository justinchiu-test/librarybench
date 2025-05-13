import pytest
from scheduler.metrics import Metrics

def test_metrics_counts_and_latencies():
    m = Metrics()
    assert m.success_count('task1') == 0
    assert m.failure_count('task1') == 0
    m.increment_success('task1')
    m.increment_failure('task1')
    assert m.success_count('task1') == 1
    assert m.failure_count('task1') == 1
    m.set_queue_length('task1', 5)
    assert m.queue_length('task1') == 5
    m.observe_latency('task1', 0.123)
    m.observe_latency('task1', 0.456)
    lat = m.latencies('task1')
    assert lat == [0.123, 0.456]

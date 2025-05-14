import pytest
from iot_scheduler.metrics import export_metrics

def test_metrics_counts_and_latencies():
    m = export_metrics()
    m.inc_push_count('group1')
    m.inc_push_count('group1')
    assert m.push_counts['group1'] == 2
    m.observe_latency('group1', 0.1)
    m.observe_latency('group1', 0.2)
    assert m.latencies['group1'] == [0.1, 0.2]
    m.inc_success('group1')
    m.inc_failure('group1')
    assert m.success_counts['group1'] == 1
    assert m.failure_counts['group1'] == 1

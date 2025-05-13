import pytest
from task_queue.metrics import MetricsIntegration

def test_queue_depth():
    m = MetricsIntegration()
    assert m.get_queue_depth('A') == 0
    m.inc_queue_depth('A')
    assert m.get_queue_depth('A') == 1
    m.dec_queue_depth('A')
    assert m.get_queue_depth('A') == 0

def test_latency():
    m = MetricsIntegration()
    assert m.get_average_latency() == 0
    m.record_latency(0.5)
    m.record_latency(1.5)
    assert pytest.approx(m.get_average_latency(), 0.001) == 1.0

def test_retry_and_error():
    m = MetricsIntegration()
    assert m.get_retry_count('T') == 0
    assert m.get_error_rate('T') == 0
    m.inc_retry('T')
    m.inc_error('T')
    m.inc_error('T')
    assert m.get_retry_count('T') == 1
    assert m.get_error_rate('T') == 2

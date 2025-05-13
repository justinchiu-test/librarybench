from iot.metrics import Metrics

def test_metrics_recording():
    m = Metrics()
    m.record_success()
    m.record_success()
    m.record_failure()
    m.record_retry("task1")
    m.record_retry("task1")
    m.record_latency(0.5)
    m.record_latency(1.5)
    summary = m.summary()
    assert summary['success_count'] == 2
    assert summary['failure_count'] == 1
    assert summary['retry_counts']['task1'] == 2
    assert abs(summary['avg_latency'] - 1.0) < 1e-6

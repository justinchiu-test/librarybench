from postscheduler.metrics import expose_metrics

def test_expose_metrics_contains_counters():
    data, content_type = expose_metrics()
    text = data.decode('utf-8')
    assert 'post_duration_seconds' in text
    assert 'queue_length' in text
    assert 'success_count' in text
    assert 'failure_count' in text
    assert 'text/plain' in content_type

from retry.hooks import MetricsHook

def test_metrics_hook():
    hook = MetricsHook()
    hook.on_retry({'delay': 1.5})
    hook.on_retry({'delay': 2.5})
    assert hook.retry_count == 2
    assert hook.latencies == [1.5, 2.5]

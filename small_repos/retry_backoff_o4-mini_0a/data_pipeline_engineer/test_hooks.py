from retrylib.hooks import OnRetryHook, MetricsHook

def test_on_retry_hook():
    calls = []
    def cb(attempt, exception, delay, context):
        calls.append((attempt, str(exception), delay))
    hook = OnRetryHook(cb)
    hook(1, Exception("err"), 0.5, None)
    assert calls == [(1, "err", 0.5)]

def test_metrics_hook():
    hook = MetricsHook()
    hook(1, Exception(), 0.1, None)
    hook(2, Exception(), 0.2, None)
    assert hook.attempts == 2
    assert hook.delays == [0.1, 0.2]

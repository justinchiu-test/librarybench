import pytest
from retry.hooks import OnRetryHook, MetricsHook, RetryHistoryCollector

def test_on_retry_hook():
    calls = []
    hook = OnRetryHook(lambda a, e, d, c: calls.append((a, e, d, c)))
    hook.on_retry(1, Exception("err"), 0.1, {'id': 123})
    assert len(calls) == 1
    attempt, exc, delay, context = calls[0]
    assert attempt == 1
    assert isinstance(exc, Exception)
    assert delay == 0.1
    assert context == {'id': 123}

def test_metrics_hook_success_and_failure():
    hook = MetricsHook()
    hook.on_start()
    hook.on_retry(1, Exception(), 0.1, {})
    hook.on_retry(2, Exception(), 0.2, {})
    hook.on_success(3, "ok", {})
    assert hook.retry_count == 2
    assert hook.success
    assert hook.latency is not None

    hook2 = MetricsHook()
    hook2.on_start()
    hook2.on_failure(1, Exception(), {})
    assert hook2.failure_count == 1
    assert hook2.latency is not None

def test_history_collector():
    hook = RetryHistoryCollector()
    ctx = {'svc': 'a'}
    hook.on_retry(1, ValueError("x"), 0.5, ctx)
    hook.on_success(2, "res", ctx)
    hook.on_failure(3, RuntimeError("e"), ctx)
    assert hook.history[0]['event'] == 'retry'
    assert hook.history[1]['event'] == 'success'
    assert hook.history[2]['event'] == 'failure'
    for entry in hook.history:
        assert 'context' in entry and entry['context'] == ctx

import pytest
from retry.backoff import ExponentialBackoffStrategy
from retry.stop_condition import MaxAttemptsStopCondition
from retry.manager import RetryManager
from retry.hooks import OnRetryHook, MetricsHook, RetryHistoryCollector

def test_retry_manager_success():
    attempts = []
    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise ValueError("fail")
        return "ok"

    backoff = ExponentialBackoffStrategy(base=0)
    stop = MaxAttemptsStopCondition(max_attempts=5)
    on_retry_calls = []
    metrics = MetricsHook()
    history = RetryHistoryCollector()
    hook = OnRetryHook(lambda a, e, d, c: on_retry_calls.append(a))
    mgr = RetryManager(backoff, stop, hooks=[hook, metrics, history], context={'id': 42}, sleep_func=lambda x: None)
    with mgr as m:
        result = m.call(flaky)
    assert result == "ok"
    assert on_retry_calls == [1, 2]
    assert metrics.retry_count == 2
    assert metrics.success
    assert history.history[0]['event'] == 'retry'
    assert history.history[-1]['event'] == 'success'
    # context preserved
    assert history.history[0]['context'] == {'id': 42}

def test_retry_manager_failure():
    def always_fail():
        raise RuntimeError("oops")

    backoff = ExponentialBackoffStrategy(base=0)
    stop = MaxAttemptsStopCondition(max_attempts=2)
    metrics = MetricsHook()
    history = RetryHistoryCollector()
    mgr = RetryManager(backoff, stop, hooks=[metrics, history], context={'x': 'y'}, sleep_func=lambda x: None)
    with pytest.raises(RuntimeError):
        with mgr as m:
            m.call(always_fail)
    # max attempts = 2, so 2 tries: 1 retry before stop, then failure
    assert metrics.retry_count == 1
    assert metrics.failure_count == 1
    assert history.history[-1]['event'] == 'failure'
    assert history.history[-1]['context'] == {'x': 'y'}

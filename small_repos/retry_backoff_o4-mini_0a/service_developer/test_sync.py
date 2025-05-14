import pytest
from retry.backoff import ExponentialBackoffStrategy
from retry.stop import MaxAttemptsStopCondition
from retry.hooks import MetricsHook
from retry.history import RetryHistoryCollector
from retry.sync import Retry, RetryContextManager

def test_retry_success_after_retries(monkeypatch):
    counter = {'count': 0}
    def flaky():
        counter['count'] += 1
        if counter['count'] < 3:
            raise ValueError("fail")
        return "ok"
    backoff = ExponentialBackoffStrategy(base=0)
    stop = MaxAttemptsStopCondition(5)
    metrics = MetricsHook()
    history = RetryHistoryCollector()
    retry = Retry(backoff, stop, hooks=[metrics], history_collector=history)
    func = retry(flaky)
    assert func() == "ok"
    assert metrics.retry_count == 2
    # 2 failures + 1 success
    assert len(history.history) == 3
    assert history.history[-1]['success'] is True

def test_retry_exhausts():
    backoff = ExponentialBackoffStrategy(base=0)
    stop = MaxAttemptsStopCondition(2)
    history = RetryHistoryCollector()
    retry = Retry(backoff, stop, history_collector=history)
    @retry
    def always_fail():
        raise RuntimeError("err")
    with pytest.raises(RuntimeError):
        always_fail()
    assert len(history.history) == 2
    assert history.history[-1]['success'] is False

def test_context_manager_call():
    backoff = ExponentialBackoffStrategy(base=0)
    stop = MaxAttemptsStopCondition(1)
    history = RetryHistoryCollector()
    retry = Retry(backoff, stop, history_collector=history)
    ctx = RetryContextManager(retry)
    def f():
        return 42
    with ctx as manager:
        result = manager.call(f)
    assert result == 42
    assert len(history.history) == 1

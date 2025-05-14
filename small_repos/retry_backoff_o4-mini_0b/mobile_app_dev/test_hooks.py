import pytest
from retry.hooks import OnRetryHook, AfterAttemptHook, OnGiveUpHook

def test_on_retry_hook():
    calls = []
    def fn(attempt, delay):
        calls.append((attempt, delay))
    hook = OnRetryHook(fn)
    hook(2, 1.5)
    assert calls == [(2, 1.5)]

def test_after_attempt_hook():
    calls = []
    def fn(attempt, success, exception, latency):
        calls.append((attempt,success,exception,latency))
    hook = AfterAttemptHook(fn)
    ex = Exception("err")
    hook(1,False,ex,0.2)
    assert calls == [(1, False, ex, 0.2)]

def test_on_give_up_hook():
    calls = []
    def fn(exception):
        calls.append(exception)
    hook = OnGiveUpHook(fn)
    ex = Exception("fail")
    hook(ex)
    assert calls == [ex]

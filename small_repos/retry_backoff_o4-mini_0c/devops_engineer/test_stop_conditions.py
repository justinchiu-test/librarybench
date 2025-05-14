import pytest
from retry_framework.stop_conditions import MaxAttemptsStopCondition
from retry_framework.history import RetryHistoryCollector

def test_max_attempts_stop():
    hist = RetryHistoryCollector()
    cond = MaxAttemptsStopCondition(2)
    assert not cond.should_stop(hist)
    hist.record(0,0,None,False)
    assert not cond.should_stop(hist)
    hist.record(0,0,None,False)
    assert cond.should_stop(hist)

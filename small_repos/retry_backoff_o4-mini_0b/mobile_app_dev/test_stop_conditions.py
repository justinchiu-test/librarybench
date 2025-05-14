import pytest
from retry.stop_conditions import MaxAttemptsStopCondition

def test_max_attempts_default():
    cond = MaxAttemptsStopCondition(max_attempts=3)
    assert not cond.should_stop(1,None)
    assert not cond.should_stop(2,None)
    assert cond.should_stop(3,None)
    assert cond.should_stop(4,None)

def test_env_var_override(monkeypatch):
    monkeypatch.setenv('MAX_RETRY_ATTEMPTS','5')
    cond = MaxAttemptsStopCondition(max_attempts=3)
    assert not cond.should_stop(4,None)
    assert cond.should_stop(5,None)

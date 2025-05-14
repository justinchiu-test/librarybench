import pytest
from retry_engine.stop_conditions import MaxAttemptsStopCondition

def test_max_attempts_stop_condition():
    cond = MaxAttemptsStopCondition(3)
    assert not cond.should_stop(1)
    assert not cond.should_stop(2)
    assert cond.should_stop(3)
    assert cond.should_stop(4)

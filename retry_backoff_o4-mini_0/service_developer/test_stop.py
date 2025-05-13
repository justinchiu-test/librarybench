import pytest
from retry.stop import MaxAttemptsStopCondition, StopConditionInterface

def test_max_attempts():
    cond = MaxAttemptsStopCondition(3)
    assert not cond.should_stop(1)
    assert not cond.should_stop(2)
    assert cond.should_stop(3)

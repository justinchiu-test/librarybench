import pytest
from retry_lib.conditions import MaxAttemptsStopCondition

def test_max_attempts():
    cond = MaxAttemptsStopCondition(3)
    assert not cond.should_stop(1, Exception())
    assert not cond.should_stop(2, Exception())
    assert cond.should_stop(3, Exception())
    assert cond.should_stop(4, Exception())

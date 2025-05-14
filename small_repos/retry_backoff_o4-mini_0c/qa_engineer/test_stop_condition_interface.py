import pytest
from retry_toolkit.stop_condition import StopConditionInterface

class MyStopCondition(StopConditionInterface):
    def should_stop(self, attempt, exception):
        return attempt >= 2

def test_stop_condition_interface():
    cond = MyStopCondition()
    assert not cond.should_stop(1, None)
    assert cond.should_stop(2, Exception("e"))

import pytest
from retry_toolkit.stop_condition import StopCondition

class MyStop(StopCondition):
    def __call__(self, attempts, last_exception):
        return attempts >= 2

def test_stop_condition():
    cond = MyStop()
    assert cond(1, None) is False
    assert cond(2, Exception()) is True

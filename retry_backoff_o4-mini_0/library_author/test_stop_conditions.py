import pytest
from retry_framework.stop_conditions import StopConditionInterface

class DummyStop(StopConditionInterface):
    def should_stop(self, attempt_number, elapsed_time):
        return attempt_number >= 3 or elapsed_time > 10

def test_interface_implementation():
    ds = DummyStop()
    assert ds.should_stop(1, 1) is False
    assert ds.should_stop(3, 0) is True
    assert ds.should_stop(2, 11) is True

def test_cannot_instantiate_base():
    with pytest.raises(TypeError):
        StopConditionInterface()

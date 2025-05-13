import pytest
from backpressure_control import BackpressureControl

class Dummy:
    def __init__(self):
        self.size = 0
        self.throttled = None

    def get_size(self):
        return self.size

    def throttle(self, flag):
        self.throttled = flag

def test_backpressure_throttle_on_off():
    dummy = Dummy()
    bp = BackpressureControl(max_queue_size=5)
    bp.register(dummy.get_size, dummy.throttle)
    dummy.size = 3
    bp.check()
    assert dummy.throttled is False
    dummy.size = 6
    bp.check()
    assert dummy.throttled is True
    dummy.size = 5
    bp.check()
    assert dummy.throttled is False

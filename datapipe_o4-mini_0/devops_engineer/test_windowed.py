import time
from pipeline.windowed import WindowedOperations

class FakeTime:
    def __init__(self):
        self.t = 0
    def time(self):
        return self.t

def test_windowed_operations(monkeypatch):
    ft = FakeTime()
    monkeypatch.setattr(time, 'time', ft.time)
    wo = WindowedOperations(window_size=5)
    assert wo.add(1) is None
    ft.t += 3
    assert wo.add(2) is None
    ft.t += 2
    res = wo.add(3)
    assert res == [1, 2, 3]
    assert wo.data == []

import pytest
from pipeline import Versioning, Windowing, BackpressureControl, DynamicReconfiguration, Stage

def test_versioning():
    v = Versioning()
    assert v.get_latest() is None
    v.add_version({"a":1})
    v.add_version({"b":2})
    assert v.get_latest() == {"b":2}

def test_windowing():
    stage = Windowing(window_size=2, slide=1)
    out = []
    for r in [1,2,3]:
        res = stage.process(r)
        if res is not None:
            out.append(res)
    assert out == [[1,2],[2,3]]

def test_backpressure_control():
    stage = BackpressureControl(low=1, high=2)
    stage.process(1)
    assert stage.throttled is False
    stage.process(2)
    assert stage.throttled is False
    stage.process(3)
    assert stage.throttled is True

def test_dynamic_reconfiguration():
    class ConfigStage(Stage):
        def __init__(self):
            self.threshold = 0
        def update_config(self, threshold):
            self.threshold = threshold
        def process(self, record):
            return record if record >= self.threshold else None
    cs = ConfigStage()
    dyn = DynamicReconfiguration(cs, config={"threshold":5})
    assert dyn.process(10) == 10
    dyn.reconfigure(threshold=15)
    assert dyn.process(10) is None

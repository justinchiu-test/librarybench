from pipeline import Pipeline
from stage import Stage
from backpressure_control import BackpressureControl
from memory_usage_control import MemoryUsageControl

def test_pipeline_simple():
    p = Pipeline()
    p.add_stage(Stage('double', lambda x: x * 2))
    result = p.run([1, 2, 3])
    assert result == [2, 4, 6]

def test_pipeline_with_memory_control(tmp_path):
    p = Pipeline()
    p.add_stage(Stage('to_str', lambda x: str(x)))
    spill_file = tmp_path / 'spill.txt'
    mem = MemoryUsageControl(threshold_bytes=1, spill_file_path=str(spill_file))
    p.set_memory_control(mem)
    result = p.run([1, 2])
    assert result == []
    assert spill_file.exists()
    lines = open(spill_file).read().splitlines()
    assert lines == ['1', '2']

def test_pipeline_with_backpressure():
    p = Pipeline()
    class DummySource:
        def __init__(self):
            self.queue_size = 0
            self.throttled = None
        def get_size(self):
            return self.queue_size
        def throttle(self, flag):
            self.throttled = flag
    src = DummySource()
    bp = BackpressureControl(max_queue_size=0)
    bp.register(src.get_size, src.throttle)
    p.set_backpressure(bp)
    p.add_stage(Stage('identity', lambda x: x))
    src.queue_size = 0
    out1 = p.run([1])
    assert src.throttled is False
    src.queue_size = 1
    out2 = p.run([2])
    assert src.throttled is True

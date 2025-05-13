# Combined simple test to ensure imports
from streamkit.backpressure import BackpressureControl
from streamkit.memory import MemoryUsageControl

def test_imports():
    bp = BackpressureControl(1)
    m = MemoryUsageControl(1)
    assert bp.capacity == 1
    assert m.capacity == 1

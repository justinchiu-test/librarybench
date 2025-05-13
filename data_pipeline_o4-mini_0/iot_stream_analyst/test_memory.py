from streamkit.memory import MemoryUsageControl

def test_memory_usage_control_spill():
    m = MemoryUsageControl(capacity=2)
    assert m.add(1) is True
    assert m.add(2) is True
    assert m.add(3) is False
    assert m.spilled is True

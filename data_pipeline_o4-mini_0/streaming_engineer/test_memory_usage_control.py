import os
from memory_usage_control import MemoryUsageControl

def test_memory_spill(tmp_path):
    spill_file = tmp_path / "spill.txt"
    control = MemoryUsageControl(threshold_bytes=10, spill_file_path=str(spill_file))
    data = ['a', 'b', 'c']
    # Under threshold
    result = control.check_and_spill(5, data)
    assert result == data
    assert not spill_file.exists()
    # Over threshold
    result2 = control.check_and_spill(20, data)
    assert result2 == []
    assert spill_file.exists()
    with open(spill_file) as f:
        lines = f.read().splitlines()
        assert lines == data

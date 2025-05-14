import pytest
from iot_fleet_manager.iot.backup import BackupManager

def test_snapshot_and_restore():
    state = {'a': 1, 'b': [1,2,3]}
    bm = BackupManager()
    snap = bm.snapshot(state)
    restored = bm.restore(snap)
    assert restored == state

def test_restore_no_snapshot():
    bm = BackupManager()
    with pytest.raises(ValueError):
        bm.restore()

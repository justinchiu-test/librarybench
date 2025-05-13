import os
import tempfile
from iotdb.snapshot import Snapshot

def test_snapshot_save_load(tmp_path):
    path = tmp_path / 'snap.bin'
    snap = Snapshot(str(path))
    state = {'a':1}
    snap.save(state)
    loaded = snap.load()
    assert loaded == state

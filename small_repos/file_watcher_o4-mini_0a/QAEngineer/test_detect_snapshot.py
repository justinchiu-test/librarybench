import os
import tempfile
import pytest
from watcher.watcher import Watcher

def test_snapshot_and_changes(tmp_path):
    # create initial files
    dir1 = tmp_path / 'd1'
    dir1.mkdir()
    f1 = dir1 / 'a.txt'
    f1.write_text('hello')
    w = Watcher(paths=[str(tmp_path)], poll_interval=0.01, debounce_interval=0)
    snap1 = w._take_snapshot()
    # modify file
    f1.write_text('world')
    snap2 = w._take_snapshot()
    events = w._detect_changes(snap1, snap2)
    assert any(e[0].endswith('a.txt') and e[1] == 'modify' for e in events)
    # create new file
    f2 = dir1 / 'b.txt'
    f2.write_text('new')
    snap3 = w._take_snapshot()
    events2 = w._detect_changes(snap2, snap3)
    assert any(e[0].endswith('b.txt') and e[1] == 'create' for e in events2)
    # delete file
    f2.unlink()
    snap4 = w._take_snapshot()
    events3 = w._detect_changes(snap3, snap4)
    assert any(e[0].endswith('b.txt') and e[1] == 'delete' for e in events3)

import time
import os
from sync_tool.snapshot import Snapshot

def create_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def test_snapshot_diff(tmp_path):
    d = tmp_path / 'dir'
    d.mkdir()
    f1 = d / 'a.txt'
    f2 = d / 'b.txt'
    create_file(f1, 'hello')
    create_file(f2, 'world')
    snap1 = Snapshot(str(d))
    time.sleep(0.01)
    create_file(f1, 'hello!')
    f3 = d / 'c.txt'
    create_file(f3, 'new')
    os.remove(f2)
    snap2 = Snapshot(str(d))
    diff = snap2.diff(snap1)
    assert sorted(diff['added']) == ['c.txt']
    assert sorted(diff['modified']) == ['a.txt']
    assert sorted(diff['removed']) == ['b.txt']

def test_snapshot_hash(tmp_path):
    d = tmp_path / 'dir'
    d.mkdir()
    f = d / 'file.bin'
    with open(f, 'wb') as fp:
        fp.write(b'data')
    snap1 = Snapshot(str(d), file_hash=True)
    snap2 = Snapshot(str(d), file_hash=True)
    diff = snap2.diff(snap1)
    assert diff['added'] == []
    assert diff['modified'] == []
    assert diff['removed'] == []
    with open(f, 'wb') as fp:
        fp.write(b'other')
    snap3 = Snapshot(str(d), file_hash=True)
    diff2 = snap3.diff(snap1)
    assert diff2['modified'] == ['file.bin']

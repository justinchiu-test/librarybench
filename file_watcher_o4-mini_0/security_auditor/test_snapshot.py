import hashlib
from pathlib import Path
import pytest
from watcher.snapshot import Snapshot

def hash_bytes(b):
    return hashlib.sha256(b).hexdigest()

def test_take_snapshot(tmp_path):
    # create files
    (tmp_path/"a.txt").write_text("hello")
    sub = tmp_path/"subdir"
    sub.mkdir()
    (sub/"b.txt").write_text("world")
    snap = Snapshot(tmp_path).take()
    assert snap == {"a.txt": hash_bytes(b"hello"), "subdir/b.txt": hash_bytes(b"world")}

def test_gitignore(tmp_path):
    (tmp_path/".gitignore").write_text("ignored.txt\n#comment")
    (tmp_path/"ignored.txt").write_text("x")
    (tmp_path/"keep.txt").write_text("y")
    snap = Snapshot(tmp_path).take()
    assert "keep.txt" in snap
    assert "ignored.txt" not in snap

def test_diff():
    old = {"a": "1", "b": "2"}
    new = {"b": "3", "c": "4"}
    d = Snapshot.diff(old, new)
    assert sorted(d["added"]) == ["c"]
    assert sorted(d["removed"]) == ["a"]
    assert sorted(d["changed"]) == ["b"]

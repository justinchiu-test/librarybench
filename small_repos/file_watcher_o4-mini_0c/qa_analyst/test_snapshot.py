import os
import tempfile
import json
import time
import pytest
from watcher.snapshot import take_snapshot, diff_snapshots

def test_empty_directory(tmp_path):
    d = tmp_path / "empty"
    d.mkdir()
    snap = take_snapshot(str(d))
    assert snap == {}

def test_snapshot_and_diff(tmp_path):
    d = tmp_path / "test"
    d.mkdir()
    f1 = d / "a.txt"
    f1.write_text("hello")
    snap1 = take_snapshot(str(d))
    time.sleep(0.01)
    f1.write_text("world")
    f2 = d / "b.txt"
    f2.write_text("new")
    snap2 = take_snapshot(str(d))
    diff = diff_snapshots(snap1, snap2, directory=str(d))
    assert "b.txt" in diff["added"]
    assert "a.txt" in diff["modified"]
    assert diff["removed"] == []

def test_diff_with_hash(tmp_path):
    d = tmp_path / "testh"
    d.mkdir()
    f = d / "f.txt"
    f.write_text("x")
    snap1 = take_snapshot(str(d))
    f.write_text("x")  # same content
    snap2 = take_snapshot(str(d))
    diff = diff_snapshots(snap1, snap2, directory=str(d), hash_compare=True)
    assert diff["modified"] == []

import pytest
from watcher import InlineDiffs
import tempfile
import os

def test_diff_creation_and_modification(tmp_path):
    diffs = InlineDiffs()
    file_path = tmp_path / "sample.md"
    # on creation, old is empty []
    file_path.write_text("line1\n")
    d1 = diffs.diff(str(file_path))
    assert "line1" in d1
    # modify file
    file_path.write_text("line1\nline2\n")
    d2 = diffs.diff(str(file_path))
    assert "+line2" in d2

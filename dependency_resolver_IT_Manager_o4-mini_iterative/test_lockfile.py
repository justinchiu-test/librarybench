import json
import os
import pytest
from lockfile import generate_lockfile, load_lockfile

def test_lockfile_roundtrip(tmp_path):
    data = {"A": "1.0.0", "B": "2.5"}
    p = tmp_path / "lock.json"
    generate_lockfile(data, str(p))
    assert p.exists()
    loaded = load_lockfile(str(p))
    assert loaded == data
    # check JSON formatting
    content = p.read_text()
    # should be pretty-printed with spaces
    assert '"A": "1.0.0"' in content
    assert content.strip().startswith("{")

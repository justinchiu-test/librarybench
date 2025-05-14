from pathlib import Path
import pytest
from watcher.filter import DynamicFilter

def test_hidden_excluded(tmp_path):
    f = tmp_path / ".secret"
    f.write_text("data")
    flt = DynamicFilter()
    assert not flt.match(f)

def test_exclude_pattern(tmp_path):
    f = tmp_path / "foo.log"
    f.write_text("log")
    flt = DynamicFilter(exclude=["*.log"])
    assert not flt.match(f)
    assert flt.match(tmp_path / "foo.txt")

def test_include_pattern(tmp_path):
    f1 = tmp_path / "a.py"
    f2 = tmp_path / "b.txt"
    f1.write_text("")
    f2.write_text("")
    flt = DynamicFilter(include=["*.py"])
    assert flt.match(f1)
    assert not flt.match(f2)

def test_dynamic_add(tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("")
    flt = DynamicFilter()
    assert flt.match(f)
    flt.add_exclude("*.txt")
    assert not flt.match(f)

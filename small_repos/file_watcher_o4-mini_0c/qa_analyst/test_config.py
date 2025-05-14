import tempfile
import json
import os
import pytest
from watcher.config import load_config

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)

def test_json(tmp_path):
    p = tmp_path / "c.json"
    data = {"a": 1}
    write_file(str(p), json.dumps(data))
    cfg = load_config(str(p))
    assert cfg == data

def test_yaml(tmp_path):
    p = tmp_path / "c.yaml"
    content = "a: 2\nb: [1,2,3]"
    write_file(str(p), content)
    cfg = load_config(str(p))
    assert cfg["a"] == 2
    assert cfg["b"] == [1,2,3]

def test_toml(tmp_path):
    p = tmp_path / "c.toml"
    content = 'a = 3\nb = ["x","y"]'
    write_file(str(p), content)
    cfg = load_config(str(p))
    assert cfg["a"] == 3
    assert cfg["b"] == ["x","y"]

def test_unsupported(tmp_path):
    p = tmp_path / "c.txt"
    write_file(str(p), "a=1")
    with pytest.raises(ValueError):
        load_config(str(p))

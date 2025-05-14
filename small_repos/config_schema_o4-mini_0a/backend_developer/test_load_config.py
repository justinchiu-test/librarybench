import os
import json
import tempfile
from configmanager import load_config

def test_load_json(tmp_path):
    data = {"a": 1, "b": "text"}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(data))
    cfg = load_config(str(p))
    assert cfg == data

def test_load_ini(tmp_path):
    content = "[section]\nx=1\ny=hello"
    p = tmp_path / "config.ini"
    p.write_text(content)
    cfg = load_config(str(p))
    assert "section" in cfg
    assert cfg["section"]["x"] == "1"
    assert cfg["section"]["y"] == "hello"

def test_load_yaml(tmp_path):
    import yaml
    data = {"c": 3, "d": "yes"}
    p = tmp_path / "config.yaml"
    p.write_text(yaml.safe_dump(data))
    cfg = load_config(str(p))
    assert cfg == data

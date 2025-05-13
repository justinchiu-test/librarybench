import os
import tempfile
import yaml
from config_manager.api import ConfigManager

def test_load_and_serialize(tmp_path):
    content = {"one": 1, "nested": {"a": 2}}
    p = tmp_path / "cfg.yaml"
    p.write_text(yaml.safe_dump(content))
    cm = ConfigManager(defaults={"defaults": True})
    cfg = cm.load(str(p))
    assert cfg["one"] == 1
    assert cfg["defaults"] is True
    s = cm.serialize()
    assert "one: 1" in s
    assert "defaults: true" in s

def test_get_set():
    cm = ConfigManager()
    cm.set("x", 100)
    assert cm.get("x") == 100

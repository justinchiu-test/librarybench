import os
from src.personas.backend_dev.microcli.env import env_override

def test_override_str(tmp_path, monkeypatch):
    config = {"x": "foo", "y": "bar"}
    monkeypatch.setenv("P_X", "baz")
    new = env_override(config, "p")
    assert new["x"] == "baz"
    assert new["y"] == "bar"

def test_override_int(monkeypatch):
    config = {"count": 5}
    monkeypatch.setenv("C_COUNT", "10")
    new = env_override(config, "c")
    assert new["count"] == 10

def test_override_bool(monkeypatch):
    config = {"flag": False}
    monkeypatch.setenv("F_FLAG", "true")
    new = env_override(config, "f")
    assert new["flag"] is True

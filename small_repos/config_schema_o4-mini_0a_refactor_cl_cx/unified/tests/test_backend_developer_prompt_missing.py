import pytest
from configschema import ConfigManager
def test_prompt(monkeypatch):
    # initialize with empty config
    cfg = ConfigManager({})
    inputs = iter(["val1", "val2"])
    monkeypatch.setattr("builtins.input", lambda prompt='': next(inputs))
    cfg.prompt_missing(["k1", "k2"])
    assert cfg.get("k1") == "val1"
    assert cfg.get("k2") == "val2"

import pytest
from backend_developer.configmanager import ConfigManager, prompt_missing
def test_prompt(monkeypatch):
    ConfigManager._config = {}
    inputs = iter(["val1", "val2"])
    monkeypatch.setattr("builtins.input", lambda prompt='': next(inputs))
    prompt_missing(["k1","k2"])
    assert ConfigManager.get("k1") == "val1"
    assert ConfigManager.get("k2") == "val2"

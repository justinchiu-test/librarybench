import builtins
from config_framework.cli import confirm_setting

def test_confirm_setting_yes(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda _: "y")
    assert confirm_setting("k", "v") is True

def test_confirm_setting_no(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda _: "n")
    assert confirm_setting("k", "v") is False

import subprocess
from devops_cli.publish import publish_package

class DummyComplete:
    def __init__(self, code):
        self.returncode = code

def test_publish_success(monkeypatch):
    def fake_run(cmd, capture_output=True, text=True):
        return DummyComplete(0)
    monkeypatch.setattr(subprocess, "run", fake_run)
    assert publish_package("dist", None) is True

def test_publish_fail(monkeypatch):
    def fake_run(cmd, capture_output=True, text=True):
        return DummyComplete(1)
    monkeypatch.setattr(subprocess, "run", fake_run)
    assert publish_package("dist", "http://repo") is False

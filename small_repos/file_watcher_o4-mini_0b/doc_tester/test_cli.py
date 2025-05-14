import pytest
import sys
from watcher import Watcher

def test_cli_main(monkeypatch):
    import cli
    fake_args = ["cli.py", "docs", "--endpoint", "http://example.com"]
    monkeypatch.setattr(sys, "argv", fake_args)
    called = {"started": False}
    def fake_start(self):
        called["started"] = True
    monkeypatch.setattr(Watcher, "start", fake_start)
    cli.main()
    assert called["started"]

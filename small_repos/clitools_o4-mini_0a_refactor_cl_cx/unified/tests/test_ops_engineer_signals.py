import sys
from io import StringIO
import pytest
from ops_engineer.cli_toolkit.signals import register_cleanup, catch_signals

def test_signal_cleanup_and_message(monkeypatch, capsys):
    calls = []
    def cleanup():
        calls.append("cleaned")
    register_cleanup(cleanup)

    @catch_signals
    def func():
        raise KeyboardInterrupt()

    result = func()
    captured = capsys.readouterr()
    assert "aborted" in captured.out
    assert calls == ["cleaned"]
    assert result is None

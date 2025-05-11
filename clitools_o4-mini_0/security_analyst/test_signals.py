import logging
import signal
import pytest
from cli_framework.signals import handle_signals

def test_handle_signals():
    logs = []
    class DummyLogger:
        def error(self, msg):
            logs.append(msg)
    def revoke():
        logs.append("revoked")
    handler = handle_signals(revoke, DummyLogger())
    with pytest.raises(SystemExit):
        handler(signal.SIGINT, None)
    assert "revoked" in logs
    assert "aborted for security" in logs

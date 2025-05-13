import signal
import pytest
from adapters.security_analyst.cli_framework.signals import handle_signals

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
    assert any("aborted for security" in msg for msg in logs)
import signal
import sys
from adapters.devops_engineer.devops_cli.signal_handler import handle_signals

def test_handle_signals(monkeypatch):
    cleaned = []
    def cleanup():
        cleaned.append(True)
    handlers = {}
    def fake_signal(sig, handler):
        handlers[sig] = handler
    monkeypatch.setattr(signal, "signal", fake_signal)
    h = handle_signals(cleanup)
    assert signal.SIGINT in handlers
    # simulate signal
    handlers[signal.SIGINT](signal.SIGINT, None)
    assert cleaned
import signal
from backend_dev.microcli.signals import handle_signals

def test_handlers_registered(tmp_path):
    called = {"ok": False}
    def cleanup():
        called["ok"] = True
    handler = handle_signals(cleanup)
    # simulate signal
    handler(signal.SIGINT, None)
    assert called["ok"]
    # check registry
    assert signal.getsignal(signal.SIGINT) == handler
    assert signal.getsignal(signal.SIGTERM) == handler

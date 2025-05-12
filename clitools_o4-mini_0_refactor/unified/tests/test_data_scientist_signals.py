import signal
from data_scientist.datapipeline_cli.signals import handle_signals, _get_registered

def test_handle_signals(monkeypatch):
    calls = []
    def cb():
        calls.append(1)
    recorded = {}
    def fake_signal(sig, handler):
        recorded[sig] = handler
    monkeypatch.setattr(signal, 'signal', fake_signal)
    res = handle_signals(cb)
    assert res is True
    # check handlers registered for SIGINT and SIGTERM
    assert signal.SIGINT in recorded
    assert signal.SIGTERM in recorded
    # simulate signal
    recorded[signal.SIGINT](None, None)
    assert calls == [1]
    # internal registry
    assert cb in _get_registered()

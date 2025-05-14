import sys
from osscli.signals import handle_signals
def test_handle_signals(capsys):
    handler = handle_signals("cmd")
    handler(2, None)
    captured = capsys.readouterr()
    assert "Cleanup after cmd" in captured.out

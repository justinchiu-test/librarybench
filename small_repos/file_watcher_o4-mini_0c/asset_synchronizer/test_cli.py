import sys
import pytest
import sync_tool.cli as cli_mod

class DummyResp:
    def __init__(self, status_code, json_data=None, text=''):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text
    def json(self):
        return self._json

def test_cli_sync_success(monkeypatch, capsys):
    def fake_post(url, json):
        return DummyResp(202, {'job_id':'id1'})
    monkeypatch.setattr(cli_mod.requests, 'post', fake_post)
    argv = sys.argv
    sys.argv = ['prog', 'sync']
    try:
        cli_mod.main()
    except SystemExit as e:
        pytest.fail(f"Unexpected exit: {e}")
    captured = capsys.readouterr()
    assert 'Started job id1' in captured.out
    sys.argv = argv

def test_cli_sync_error(monkeypatch, capsys):
    def fake_post(url, json):
        return DummyResp(400, text='err')
    monkeypatch.setattr(cli_mod.requests, 'post', fake_post)
    argv = sys.argv
    sys.argv = ['prog', 'sync']
    with pytest.raises(SystemExit) as e:
        cli_mod.main()
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert 'Error' in captured.err
    sys.argv = argv

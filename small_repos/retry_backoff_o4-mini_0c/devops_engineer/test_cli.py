import sys
import json
import tempfile
from retry_framework.cli import main
from retry_framework.config import ConfigFileSupport

def test_cli_validate(tmp_path, capsys, monkeypatch):
    data = {'x': 1}
    path = tmp_path / 'conf.json'
    path.write_text(json.dumps(data))
    monkeypatch.setattr(sys, 'argv', ['retry-cli', 'validate', str(path)])
    main()
    captured = capsys.readouterr()
    assert json.loads(captured.out) == data

def test_cli_simulate(tmp_path, capsys, monkeypatch):
    data = {'y': 2}
    path = tmp_path / 'conf.json'
    path.write_text(json.dumps(data))
    monkeypatch.setattr(sys, 'argv', ['retry-cli', 'simulate', str(path)])
    main()
    captured = capsys.readouterr()
    assert 'Simulated 1 attempts' in captured.out

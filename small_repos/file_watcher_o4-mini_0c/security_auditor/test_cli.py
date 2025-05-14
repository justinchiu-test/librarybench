import sys
import json
from pathlib import Path
import pytest
from watcher.cli import main

def test_cli_output(tmp_path, monkeypatch, capsys):
    # setup directory
    d = tmp_path
    (d/"one.txt").write_text("1")
    (d/"two.txt").write_text("2")
    monkeypatch.setattr(sys, 'argv', ['prog', str(d)])
    main()
    captured = capsys.readouterr()
    out = json.loads(captured.out)
    assert "one.txt" in out and "two.txt" in out

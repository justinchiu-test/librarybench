import subprocess
import sys
import json
import tempfile
import os
from watcher.cli import main

def test_cli_snapshot_diff(tmp_path, monkeypatch, capsys):
    # create directory and files
    d = tmp_path / "cli"
    d.mkdir()
    f = d / "t.txt"
    f.write_text("hi")
    # snapshot
    monkeypatch.setattr(sys, 'argv', ['watcher', 'snapshot', str(d)])
    main()
    out = capsys.readouterr().out
    snap = json.loads(out)
    assert "t.txt" in snap
    # write new file
    f2 = d / "u.txt"
    f2.write_text("hello")
    # save snapshots to files
    old = tmp_path / "old.json"
    new = tmp_path / "new.json"
    old.write_text(json.dumps(snap))
    # take new
    monkeypatch.setattr(sys, 'argv', ['watcher', 'snapshot', str(d)])
    main()
    out2 = capsys.readouterr().out
    new_snap = json.loads(out2)
    new.write_text(json.dumps(new_snap))
    # diff
    monkeypatch.setattr(sys, 'argv', ['watcher', 'diff', str(old), str(new)])
    main()
    diff = json.loads(capsys.readouterr().out)
    assert "u.txt" in diff["added"]

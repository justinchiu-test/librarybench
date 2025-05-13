import subprocess
import pytest
from devops_engineer.devops_cli.bump import bump_version

class DummyResult:
    def __init__(self, stdout):
        self.stdout = stdout

def test_bump_version(monkeypatch):
    calls = []
    def fake_run(cmd, capture_output=False, text=False, check=False):
        if cmd[:3] == ['git', 'tag', '--sort=-v:refname']:
            return DummyResult("v1.2.3\nv1.2.2\n")
        if cmd[0:2] == ['git', 'tag']:
            calls.append(cmd)
            return DummyResult("")
        raise RuntimeError("Unexpected cmd")
    monkeypatch.setattr(subprocess, "run", fake_run)
    new_ver = bump_version()
    assert new_ver == "1.2.4"
    assert any("-a" in c or "-a" not in c for c in calls)

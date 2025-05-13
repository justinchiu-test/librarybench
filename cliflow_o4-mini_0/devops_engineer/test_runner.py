import subprocess
import pytest
from cli_framework.context import Context
from cli_framework.runner import run_dry_run

def test_run_dry_run_print(capsys):
    ctx = Context()
    ctx.dry_run = True
    result = run_dry_run(ctx, "echo hi")
    captured = capsys.readouterr()
    assert "DRY RUN: echo hi" in captured.out
    assert result.returncode == 0

def test_run_execute():
    ctx = Context()
    ctx.dry_run = False
    res = run_dry_run(ctx, "echo hi")
    assert isinstance(res, subprocess.CompletedProcess)
    assert res.returncode == 0

def test_hooks():
    ctx = Context()
    calls = []
    def pre(cmd):
        calls.append(('pre', cmd))
    def post(cmd, res):
        calls.append(('post', cmd))
    ctx.register_hook('pre-command', pre)
    ctx.register_hook('post-command', post)
    ctx.dry_run = False
    _ = run_dry_run(ctx, "echo hi")
    assert ('pre', "echo hi") in calls
    assert ('post', "echo hi") in calls

import sys
from io import StringIO
import pytest
from sre.task_queue.cli import main

def run_cli(args):
    old = sys.stdout
    sys.stdout = StringIO()
    try:
        main(args)
        return sys.stdout.getvalue()
    finally:
        sys.stdout = old

def test_cli_quota():
    out = run_cli(['quota', 'svc', '5'])
    assert 'Quota for svc set to 5' in out

def test_cli_pause_resume():
    out1 = run_cli(['pause', 'Tenant1'])
    assert 'Paused queue for Tenant1' in out1
    out2 = run_cli(['resume', 'Tenant1'])
    assert 'Resumed queue for Tenant1' in out2

def test_cli_list_empty():
    out = run_cli(['list'])
    assert out == ''

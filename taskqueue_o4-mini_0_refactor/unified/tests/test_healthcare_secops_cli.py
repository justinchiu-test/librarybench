import pytest
import sys
from io import StringIO
import healthcare_secops.cli as cli

def run_cmd(args, audit_file):
    cli.auditor.filename = audit_file
    stdout = StringIO()
    stderr = StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = stdout, stderr
        code = cli.main(args)
    finally:
        sys.stdout, sys.stderr = old_out, old_err
    return code, stdout.getvalue(), stderr.getvalue()

def test_enqueue_and_tail(tmp_path):
    audit_file = str(tmp_path / "audit.log")
    code, out, err = run_cmd(['enqueue'], audit_file)
    assert code == 0
    assert out.startswith("Enqueued ")
    task_id = out.strip().split()[1]
    code2, out2, err2 = run_cmd(['tail-logs'], audit_file)
    assert code2 == 0
    assert task_id in out2

def test_cancel_without_id(tmp_path):
    audit_file = str(tmp_path / "audit.log")
    code, out, err = run_cmd(['cancel'], audit_file)
    assert code == 1
    assert "Task ID required" in err

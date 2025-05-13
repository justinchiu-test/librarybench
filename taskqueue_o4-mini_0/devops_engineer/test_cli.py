import os
import sys
from taskqueue.queue import TaskQueue
import cli

def run_cli(argv, data_dir):
    sys_argv = ['prog'] + argv + ['--data-dir', data_dir]
    sys.argv = sys_argv
    from io import StringIO
    import sys as _sys
    old = _sys.stdout
    out = StringIO()
    _sys.stdout = out
    try:
        cli.main()
    finally:
        _sys.stdout = old
    return out.getvalue().strip()

def test_cli_enqueue_and_stats(tmp_path):
    data_dir = str(tmp_path)
    out = run_cli(['enqueue', 'hello'], data_dir)
    assert len(out) > 0
    out2 = run_cli(['stats'], data_dir)
    assert 'pending: 1' in out2.lower()

def test_cli_cancel_and_tail_logs(tmp_path):
    data_dir = str(tmp_path)
    tid = run_cli(['enqueue', 'hello'], data_dir)
    out = run_cli(['cancel', tid], data_dir)
    assert 'canceled' in out.lower()
    out2 = run_cli(['tail-logs'], data_dir)
    assert 'enqueue' in out2
    assert 'cancel' in out2

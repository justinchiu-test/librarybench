import sys
from cli import main
import pytest
import json
from io import StringIO

def run_cli(args):
    old_argv = sys.argv
    old_stdout = sys.stdout
    sys.argv = ['cli'] + args
    sys.stdout = StringIO()
    try:
        main()
        output = sys.stdout.getvalue().strip()
    finally:
        sys.argv = old_argv
        sys.stdout = old_stdout
    return output

def test_enqueue_cli():
    payload = '{"a":2}'
    out = run_cli(['enqueue', '--payload', payload])
    import uuid
    uuid.UUID(out)

def test_cancel_cli():
    out = run_cli(['cancel', '--id', 'nonexistent'])
    assert out == 'not found'

def test_metrics_cli():
    out = run_cli(['metrics'])
    data = json.loads(out)
    assert 'throughput' in data

def test_logs_cli():
    out = run_cli(['logs'])
    data = json.loads(out)
    assert isinstance(data, list)

import subprocess
import sys
import json
import os
import pytest

from cli import main

def capture_output(args):
    from io import StringIO
    import sys
    backup = sys.stdout
    sys.stdout = StringIO()
    try:
        main(args)
        return sys.stdout.getvalue().strip()
    finally:
        sys.stdout = backup

def test_cli_scaffold():
    out = capture_output(["scaffold_pipeline"])
    data = json.loads(out)
    assert data["pipeline_name"] == "pipeline"

def test_cli_run_stream():
    out = capture_output(["run_pipeline", "--stream"])
    assert "Pipeline running, stream=True" in out

def test_cli_enable_streaming():
    out = capture_output(["enable_streaming"])
    assert "Streaming enabled: True" in out

def test_cli_set_skip():
    out = capture_output(["set_skip_on_error"])
    assert "Skip on error: True" in out

def test_cli_set_rate_limit():
    out = capture_output(["set_rate_limit", "250"])
    assert "Rate limit: 250" in out

def test_cli_exporter():
    out = capture_output(["start_prometheus_exporter"])
    assert "Exporter started: True" in out

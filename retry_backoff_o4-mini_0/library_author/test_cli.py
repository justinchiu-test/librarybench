import subprocess
import sys
import os
import pytest

def test_cli_main_help(tmp_path, capsys):
    # Call main with required args
    sys_argv = ["prog", "--endpoint", "http://example.com", "--retries", "2", "--backoff", "exponential"]
    old_argv = sys.argv
    sys.argv = sys_argv
    try:
        from retry_framework.cli import main
        ret = main()
        captured = capsys.readouterr()
        assert "Endpoint: http://example.com" in captured.out
        assert "Retries: 2" in captured.out
        assert "Backoff: exponential" in captured.out
        assert ret == 0
    finally:
        sys.argv = old_argv

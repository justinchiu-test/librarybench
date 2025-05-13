import subprocess
import sys
import os
import shutil
import pytest
from retry_toolkit.cli_utilities import run_retry_test

def test_run_retry_test_success():
    history = run_retry_test(attempts=5, failures=2)
    assert history[-1][0] == "success"
    assert len(history) == 3

def test_run_retry_test_failure():
    history = run_retry_test(attempts=3, failures=5)
    assert all(status == "fail" for status, _ in history)
    assert len(history) == 3

import os
from translator.run_test import run_test

def test_run_test_echo(tmp_path, monkeypatch):
    # Use echo command
    output = run_test(["echo", "hi"], locale="en_US")
    # echo adds newline
    assert output.strip() == "hi"

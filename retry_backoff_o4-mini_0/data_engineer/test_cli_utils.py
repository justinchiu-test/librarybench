import pytest
from retry_toolkit.cli_utils import stress_test

def test_stress_test_success(capsys):
    def succeed():
        pass
    stress_test(succeed, 3)
    captured = capsys.readouterr()
    assert "Attempt 1: Success" in captured.out
    assert "Total Successes: 3/3" in captured.out

def test_stress_test_failure(capsys):
    def flail():
        raise RuntimeError("fail")
    stress_test(flail, 2)
    captured = capsys.readouterr()
    assert "Attempt 1: Failure: fail" in captured.out
    assert "Total Successes: 0/2" in captured.out

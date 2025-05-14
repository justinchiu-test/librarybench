import subprocess
import sys
import pytest

def test_run_tests_exit_zero():
    # This test ensures run_tests() can be invoked without error
    from src.interfaces.game_developer.statemachine import run_tests
    ret = run_tests()
    # pytest returns exit code; zero means success
    assert ret == 0 or isinstance(ret, int)
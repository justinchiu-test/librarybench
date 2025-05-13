import pytest
from scheduler.sandbox import run_in_sandbox

def test_run_in_sandbox_echo():
    out, err, code = run_in_sandbox("echo hello", timeout=5)
    assert 'hello' in out
    assert err == ''
    assert code == 0

def test_run_in_sandbox_timeout():
    with pytest.raises(Exception):
        run_in_sandbox("sleep 1", timeout=0.01)

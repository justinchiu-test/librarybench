import re
import os
import tempfile
import pytest
from devops_cli.utils import compute_default, range_validator, file_exists, regex_validator, retry_call

def test_compute_default():
    ts = compute_default("timestamp")
    assert ts.endswith("Z")
    uid = compute_default("uuid")
    assert re.match(r"^[0-9a-f-]{36}$", uid)
    with pytest.raises(ValueError):
        compute_default("unknown")

def test_validators(tmp_path):
    rv = range_validator(1, 3)
    assert rv(2)
    with pytest.raises(ValueError):
        rv(0)
    f = tmp_path / "f.txt"
    f.write_text("x")
    assert file_exists(str(f))
    with pytest.raises(FileNotFoundError):
        file_exists(str(f)+"x")
    rvx = regex_validator(r"\d+")
    assert rvx("123")
    with pytest.raises(ValueError):
        rvx("abc")

def test_retry_call_success():
    calls = {"n":0}
    @retry_call(max_attempts=3, base_delay=0)
    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("fail")
        return "ok"
    assert flaky() == "ok"
    assert calls["n"] == 2

def test_retry_call_fail():
    @retry_call(max_attempts=2, base_delay=0)
    def always():
        raise RuntimeError("never")
    with pytest.raises(RuntimeError):
        always()

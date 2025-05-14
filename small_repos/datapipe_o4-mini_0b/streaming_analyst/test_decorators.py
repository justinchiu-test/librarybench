import pytest
from pipeline import retry_on_error, halt_on_error

count = {"tries": 0}

def flaky(x):
    count["tries"] += 1
    if count["tries"] < 2:
        raise ValueError("transient")
    return x * 2

@retry_on_error(retries=3)
def test_retry(x):
    return flaky(x)

@halt_on_error
def test_halt(x):
    if x < 0:
        raise RuntimeError("fail fast")
    return x + 1

def test_retry_decorator_success():
    count["tries"] = 0
    assert test_retry(5) == 10
    assert count["tries"] == 2

def test_retry_decorator_fail():
    @retry_on_error(retries=2)
    def always_fail():
        raise KeyError("oops")
    with pytest.raises(KeyError):
        always_fail()

def test_halt_on_error_pass():
    assert test_halt(3) == 4

def test_halt_on_error_fail():
    with pytest.raises(RuntimeError):
        test_halt(-1)

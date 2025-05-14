import pytest
from pipeline import debug_pipeline

def good_func(x):
    return x + 1

def bad_func(x):
    raise ValueError("oops")

def test_debug_success():
    assert debug_pipeline(good_func, 5) == 6

def test_debug_failure():
    res = debug_pipeline(bad_func, {"key": "value"})
    assert res["error"] == "oops"
    assert res["record"] == {"key": "value"}

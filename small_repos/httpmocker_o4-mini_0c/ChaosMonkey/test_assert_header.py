import pytest
import chaoslib

def test_assert_header_missing():
    req = {'headers': {}}
    with pytest.raises(AssertionError):
        chaoslib.assertHeader('X-Trace-Id', req)

def test_assert_header_present():
    req = {'headers': {'X-Trace-Id': '1234'}}
    chaoslib.assertHeader('X-Trace-Id', req)  # should not raise

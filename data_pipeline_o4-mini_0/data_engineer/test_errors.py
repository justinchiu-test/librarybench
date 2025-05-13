import pytest
from pipeline.errors import error_handling_skip, error_handling_retry

def test_skip_decorator():
    @error_handling_skip
    def stage(records):
        r = records[0]
        if r < 0:
            raise ValueError("bad")
        return [r * 2]
    out = stage([-1,2,-3,4])
    assert out == [4,8]

def test_retry_decorator():
    calls = {'count':0}
    @error_handling_retry(max_retries=2, backoff=0)
    def stage(records):
        calls['count'] += 1
        if calls['count'] < 2:
            raise ValueError("fail")
        return [records[0]+1]
    out = stage([5])
    assert out == [6]

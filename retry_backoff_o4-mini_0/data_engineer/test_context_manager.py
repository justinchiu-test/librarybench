import pytest
from retry_toolkit.context_manager import retry_context

def test_retry_context_success():
    count = {'c': 0}
    def work():
        count['c'] += 1
        if count['c'] < 2:
            raise ValueError
    with retry_context(max_attempts=3):
        work()
    assert count['c'] == 2

def test_retry_context_fail():
    count = {'c': 0}
    def work():
        count['c'] += 1
        raise ValueError
    with pytest.raises(ValueError):
        with retry_context(max_attempts=2):
            work()
    assert count['c'] == 2

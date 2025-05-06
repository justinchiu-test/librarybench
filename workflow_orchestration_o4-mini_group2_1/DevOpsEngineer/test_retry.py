import pytest
from DevOpsEngineer.tasks.retry import get_backoff_delay

def test_backoff_zero_retry():
    assert get_backoff_delay(0, 1.0) == 0.0

def test_backoff_first_attempt():
    assert get_backoff_delay(1, 2.0) == 2.0

def test_backoff_second_attempt():
    assert get_backoff_delay(2, 2.0) == 4.0

def test_backoff_third_attempt():
    assert get_backoff_delay(3, 0.5) == 0.5 * 2**2

import pytest
from Data_Engineer.workflow.utils import exponential_backoff

def test_exponential_backoff():
    assert exponential_backoff(1, 1) == 1
    assert exponential_backoff(1, 2) == 2
    assert exponential_backoff(2, 3) == 2 * 4  # 2 * (2^(3-1))

import pytest
from retry.backoff import ExponentialBackoffStrategy, FullJitterBackoffStrategy, BackoffGeneratorInterface

def test_exponential_backoff():
    strat = ExponentialBackoffStrategy(base=2, cap=10)
    assert strat(1) == 2
    assert strat(2) == 4
    assert strat(3) == 8
    assert strat(4) == 10  # capped

def test_full_jitter_backoff():
    strat = FullJitterBackoffStrategy(base=2, cap=10)
    exp = ExponentialBackoffStrategy(base=2, cap=10)
    for i in range(1,6):
        delay = strat(i)
        assert 0 <= delay <= exp(i)

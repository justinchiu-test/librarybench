import random
import pytest
from retry_lib.strategies import ExponentialBackoffStrategy, FullJitterBackoffStrategy, BackoffGeneratorInterface

def test_exponential_backoff_strategy():
    strat = ExponentialBackoffStrategy(base=1, cap=5)
    gen = strat()
    delays = [next(gen) for _ in range(4)]
    assert delays == [1, 2, 4, 5]

def test_full_jitter_backoff_strategy():
    random.seed(0)
    strat = FullJitterBackoffStrategy(base=1, cap=5)
    gen = strat()
    delays = [next(gen) for _ in range(4)]
    assert 0 <= delays[0] <= 1
    assert 0 <= delays[1] <= 2
    assert 0 <= delays[2] <= 4
    assert 0 <= delays[3] <= 5

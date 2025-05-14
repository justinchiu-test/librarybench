import pytest
import random
from retry.backoff import ExponentialBackoffStrategy, FullJitterBackoffStrategy, BackoffGeneratorInterface

def test_exponential_backoff_sequence():
    strat = ExponentialBackoffStrategy(base=1)
    delays = [strat.get_delay(i) for i in range(1, 6)]
    assert delays == [1, 2, 4, 8, 16]

def test_full_jitter_bounds(monkeypatch):
    seq = [0.0, 0.5, 1.0]
    monkeypatch.setattr(random, 'random', lambda: seq.pop(0))
    strat = FullJitterBackoffStrategy(base=2, cap=5)
    # attempt 1: exp=2, max=2 -> delay=0*2=0
    assert strat.get_delay(1) == 0.0
    # attempt 2: exp=4, max=4 -> delay=0.5*4=2.0
    assert strat.get_delay(2) == 2.0
    # attempt 3: exp=8, cap=5 -> max=5 -> delay=1.0*5=5.0
    assert strat.get_delay(3) == 5.0

def test_backoff_interface():
    assert issubclass(ExponentialBackoffStrategy, BackoffGeneratorInterface)
    assert issubclass(FullJitterBackoffStrategy, BackoffGeneratorInterface)

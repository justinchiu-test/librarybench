import os
import random
import pytest
from retry.strategies import ExponentialBackoffStrategy, FullJitterBackoffStrategy

def test_exponential_backoff_delay():
    strat = ExponentialBackoffStrategy(initial_delay=2, max_delay=10)
    assert strat.delay(1) == 2
    assert strat.delay(2) == 4
    assert strat.delay(3) == 8
    assert strat.delay(4) == 10

def test_full_jitter_backoff_delay():
    random.seed(0)
    strat = FullJitterBackoffStrategy(initial_delay=1, max_delay=5)
    cap = min(1 * 2**(3-1),5)
    val = strat.delay(3)
    assert 0 <= val <= cap

def test_env_var_overrides(monkeypatch):
    monkeypatch.setenv('EXPONENTIAL_INITIAL_DELAY','3')
    monkeypatch.setenv('EXPONENTIAL_MAX_DELAY','7')
    strat = ExponentialBackoffStrategy(initial_delay=2, max_delay=10)
    assert strat.initial_delay == 3.0
    assert strat.max_delay == 7.0
    monkeypatch.setenv('JITTER_INITIAL_DELAY','4')
    monkeypatch.setenv('JITTER_MAX_DELAY','8')
    jstrat = FullJitterBackoffStrategy(initial_delay=2, max_delay=10)
    assert jstrat.initial_delay == 4.0
    assert jstrat.max_delay == 8.0

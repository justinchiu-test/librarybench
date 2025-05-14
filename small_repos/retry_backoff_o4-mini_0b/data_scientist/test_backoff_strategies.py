import random
import pytest
from retry_engine.backoff import ExponentialBackoffStrategy, FullJitterBackoffStrategy

def test_exponential_backoff_delays():
    strat = ExponentialBackoffStrategy(base=2.0, max_delay=20.0)
    assert strat.next_delay(1) == 2.0
    assert strat.next_delay(2) == 4.0
    assert strat.next_delay(3) == 8.0
    assert strat.next_delay(5) == 20.0  # capped

def test_full_jitter_within_bounds(monkeypatch):
    calls = []
    def fake_uniform(a, b):
        calls.append((a, b))
        return b - 0.1
    monkeypatch.setattr(random, 'uniform', fake_uniform)
    strat = FullJitterBackoffStrategy(base=1.0, max_delay=5.0)
    delay = strat.next_delay(3)
    cap = strat.base * (2 ** (3 - 1))
    cap = min(cap, strat.max_delay)
    assert calls == [(0, cap)]
    assert delay == cap - 0.1

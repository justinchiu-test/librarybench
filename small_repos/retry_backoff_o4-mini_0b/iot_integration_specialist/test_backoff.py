import pytest
from retrylib.backoff import ExponentialBackoffStrategy, FullJitterBackoffStrategy

def test_exponential_backoff_strategy():
    strat = ExponentialBackoffStrategy(base=2, cap=None)
    assert strat.delay(1) == 2
    assert strat.delay(2) == 4
    assert strat.delay(3) == 8

    strat_cap = ExponentialBackoffStrategy(base=2, cap=5)
    assert strat_cap.delay(1) == 2
    assert strat_cap.delay(2) == 4
    assert strat_cap.delay(3) == 5  # capped

def test_full_jitter_backoff_strategy():
    strat = FullJitterBackoffStrategy(base=2, cap=None)
    for attempt in [1, 2, 3]:
        raw = strat.base * (2 ** (attempt - 1))
        vals = [strat.delay(attempt) for _ in range(100)]
        assert all(0 <= v <= raw for v in vals)

    strat_cap = FullJitterBackoffStrategy(base=2, cap=5)
    raw3 = min(2 * (2 ** (3 - 1)), 5)
    vals = [strat_cap.delay(3) for _ in range(100)]
    assert all(0 <= v <= raw3 for v in vals)

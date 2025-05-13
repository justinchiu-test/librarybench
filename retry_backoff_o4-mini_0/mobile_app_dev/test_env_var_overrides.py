import os
import random
import pytest
from retry.strategies import ExponentialBackoffStrategy, FullJitterBackoffStrategy
from retry.stop_conditions import MaxAttemptsStopCondition

def test_strategy_env_overrides(monkeypatch):
    monkeypatch.setenv('EXPONENTIAL_INITIAL_DELAY','5')
    monkeypatch.setenv('EXPONENTIAL_MAX_DELAY','9')
    strat = ExponentialBackoffStrategy(initial_delay=1, max_delay=2)
    assert strat.initial_delay == 5.0
    assert strat.max_delay == 9.0

    monkeypatch.setenv('JITTER_INITIAL_DELAY','2')
    monkeypatch.setenv('JITTER_MAX_DELAY','4')
    jstrat = FullJitterBackoffStrategy(initial_delay=1, max_delay=2)
    assert jstrat.initial_delay == 2.0
    assert jstrat.max_delay == 4.0

def test_stop_condition_env_override(monkeypatch):
    monkeypatch.setenv('MAX_RETRY_ATTEMPTS','7')
    cond = MaxAttemptsStopCondition(max_attempts=3)
    assert not cond.should_stop(6, None)
    assert cond.should_stop(7, None)

import pytest
from retry_framework.backoff import BackoffRegistry, exponential

def test_default_exponential():
    strat = BackoffRegistry.get('exponential')
    assert strat(1) == 1
    assert strat(2) == 2
    assert strat(3) == 4

def test_register_and_get():
    def custom(a):
        return a * 0
    BackoffRegistry.register('zero', custom)
    assert BackoffRegistry.get('zero') == custom
    assert BackoffRegistry.get('zero')(5) == 0

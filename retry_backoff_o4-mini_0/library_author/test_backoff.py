import pytest
from retry_framework.backoff import BackoffRegistry, constant_backoff, exponential_backoff

def test_constant_backoff():
    assert constant_backoff(1) == 1
    assert constant_backoff(5, base=3) == 3

def test_exponential_backoff():
    assert exponential_backoff(1) == 1
    assert exponential_backoff(3, base=2, factor=3) == 2 * 3**2

def test_registry_simple():
    assert BackoffRegistry.get("constant") is constant_backoff
    assert BackoffRegistry.get("exponential") is exponential_backoff

def test_register_custom():
    def custom(attempt):
        return attempt * 2
    BackoffRegistry.register("custom", custom)
    assert BackoffRegistry.get("custom") is custom

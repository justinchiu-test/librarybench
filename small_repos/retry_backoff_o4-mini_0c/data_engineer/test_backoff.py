import pytest
from retry_toolkit.backoff import BackoffRegistry

def test_backoff_registry():
    BackoffRegistry._registry.clear()
    BackoffRegistry.register('fast', lambda x: x * 0.1)
    func = BackoffRegistry.get('fast')
    assert func(3) == pytest.approx(0.3)

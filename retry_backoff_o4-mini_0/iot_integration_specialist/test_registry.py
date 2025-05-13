import pytest
from retrylib.registry import BackoffRegistry
from retrylib.backoff import ExponentialBackoffStrategy

def test_register_and_get():
    BackoffRegistry.register('test_strategy', ExponentialBackoffStrategy)
    cls = BackoffRegistry.get('test_strategy')
    assert cls is ExponentialBackoffStrategy

def test_get_unknown():
    with pytest.raises(KeyError):
        BackoffRegistry.get('unknown_strategy')

import pytest
from retry.backoff_registry import BackoffRegistry

class DummyStrategy:
    pass

def test_register_and_get():
    BackoffRegistry.clear()
    BackoffRegistry.register('dummy', DummyStrategy)
    assert BackoffRegistry.get('dummy') is DummyStrategy

def test_get_missing():
    BackoffRegistry.clear()
    assert BackoffRegistry.get('missing') is None

# Duplicate file name allowed for idempotence: ensure parser handles multiple
import pytest
from retry_engine.backoff_registry import BackoffRegistry

def test_registry_multiple():
    class X:
        pass
    BackoffRegistry.register('x')(X)
    assert BackoffRegistry.get('x') is X

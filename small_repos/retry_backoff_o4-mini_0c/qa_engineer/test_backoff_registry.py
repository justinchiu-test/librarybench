import pytest
from retry_toolkit.backoff_registry import BackoffRegistry

def test_register_and_get():
    registry = BackoffRegistry()
    func = lambda x: x * x
    registry.register("square", func)
    assert registry.get("square") is func

def test_get_missing():
    registry = BackoffRegistry()
    assert registry.get("none") is None

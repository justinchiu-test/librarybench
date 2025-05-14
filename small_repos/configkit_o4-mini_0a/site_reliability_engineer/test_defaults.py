import pytest
from srectl.defaults import DefaultFallback

def test_default_fallback():
    defaults = DefaultFallback().load()
    assert isinstance(defaults, dict)
    assert defaults['circuit_breaker']['error_rate'] == 0.05
    assert defaults['alert']['threshold'] == 0.9
    assert defaults['service']['timeout'] == 10
    assert isinstance(defaults['alerts'], list)

import pytest
from config.defaults import DefaultFallback

def test_apply_defaults_empty():
    config = {}
    result = DefaultFallback.apply(config)
    assert result['learning_rate'] == 0.001
    assert result['epochs'] == 10
    assert result['batch_size'] == 32

def test_apply_defaults_partial():
    config = {'learning_rate': 0.01}
    result = DefaultFallback.apply(config)
    assert result['learning_rate'] == 0.01
    assert result['epochs'] == 10
    assert result['batch_size'] == 32

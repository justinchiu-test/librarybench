import pytest
from config.base import DefaultFallback

def test_defaults_structure():
    defaults = DefaultFallback.get_defaults()
    assert 'physics' in defaults
    assert 'spawn' in defaults
    assert 'ui' in defaults
    assert isinstance(defaults['physics']['gravity'], float)
    assert isinstance(defaults['spawn']['rate'], float)
    assert isinstance(defaults['ui']['scale'], float)

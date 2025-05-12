import pytest
from config_framework.default_fallback import DefaultFallback

def test_get_existing():
    df = DefaultFallback({'a': 1})
    assert df.get('a') == 1

def test_get_missing():
    df = DefaultFallback({'a': 1})
    assert df.get('b', 2) == 2
    assert df.get('b') is None

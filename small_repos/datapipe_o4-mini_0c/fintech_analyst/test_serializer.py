import pytest
from serializer import register_serializer, get_serializer

def test_register_and_get_serializer():
    def dummy(x): return x
    register_serializer('dummy', dummy)
    assert get_serializer('dummy') is dummy

def test_register_invalid():
    with pytest.raises(ValueError):
        register_serializer('bad', None)

import pytest
from pipeline.serializer import register_serializer, get_serializer

class DummySer:
    pass

def test_register_and_get():
    register_serializer('dummy', DummySer)
    assert get_serializer('dummy') is DummySer
    assert get_serializer('none') is None

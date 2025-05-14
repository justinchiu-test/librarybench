import pytest
from telemetry.serializer import register_serializer, serialize

def test_register_and_serialize():
    def dummy(data):
        return data.upper()
    register_serializer('upper', dummy)
    out = serialize('upper', 'abc')
    assert out == 'ABC'

def test_unknown_serializer():
    with pytest.raises(KeyError):
        serialize('none', 'data')

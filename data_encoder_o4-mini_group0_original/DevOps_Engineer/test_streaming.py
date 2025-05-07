import pytest
from DevOps_Engineer.devops_utils.streaming import stream_decode

def test_stream_decode_basic():
    data_stream = [b'hello', b' ', b'world']
    decoded = ''.join(chunk for chunk in stream_decode(data_stream))
    assert decoded == 'hello world'

def test_stream_decode_bytearray():
    data_stream = [bytearray(b'test')]
    decoded = list(stream_decode(data_stream))
    assert decoded == ['test']

def test_stream_decode_invalid_type():
    data_stream = [123, b'abc']
    with pytest.raises(ValueError):
        list(stream_decode(data_stream))

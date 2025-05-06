import pytest
from endianness_handling import endianness_handling

def test_pack_int_big_endian():
    n = 1000
    b = endianness_handling(n, 'big')
    assert isinstance(b, bytes)
    assert int.from_bytes(b, 'big') == n

def test_pack_int_little_endian():
    n = 1000
    b = endianness_handling(n, 'little')
    assert isinstance(b, bytes)
    assert int.from_bytes(b, 'little') == n

def test_unpack_bytes_big_endian():
    raw = (1000).to_bytes(2, 'big')
    n = endianness_handling(raw, 'big')
    assert isinstance(n, int)
    assert n == 1000

def test_unpack_bytes_little_endian():
    raw = (1000).to_bytes(2, 'little')
    n = endianness_handling(raw, 'little')
    assert isinstance(n, int)
    assert n == 1000

def test_negative_int_error():
    with pytest.raises(ValueError):
        endianness_handling(-5, 'big')

def test_invalid_byte_order():
    with pytest.raises(ValueError):
        endianness_handling(1, 'middle')

def test_invalid_data_type():
    with pytest.raises(TypeError):
        endianness_handling(3.14, 'big')

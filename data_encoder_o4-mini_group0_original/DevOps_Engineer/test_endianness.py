import pytest
from DevOps_Engineer.devops_utils.endianness import endianness_handling

def test_endianness_int_to_bytes_big():
    value = 0x010203
    result = endianness_handling(value, endianness='big')
    assert isinstance(result, bytes)
    assert result == b'\x01\x02\x03'

def test_endianness_int_to_bytes_little():
    value = 0x010203
    result = endianness_handling(value, endianness='little')
    assert isinstance(result, bytes)
    assert result == b'\x03\x02\x01'

def test_endianness_bytes_to_int_big():
    data = b'\x04\x05\x06'
    result = endianness_handling(data, endianness='big')
    assert isinstance(result, int)
    assert result == 0x040506

def test_endianness_bytes_to_int_little():
    data = b'\x04\x05\x06'
    result = endianness_handling(data, endianness='little')
    assert result == 0x060504

def test_endianness_zero_int_roundtrip():
    # zero should produce a single 0-byte
    b = endianness_handling(0, 'big')
    assert b == b'\x00'
    # and round-trip back to zero
    assert endianness_handling(b, 'big') == 0

def test_endianness_invalid_endianness():
    with pytest.raises(ValueError):
        endianness_handling(1, endianness='middle')

def test_endianness_invalid_data_type():
    with pytest.raises(ValueError):
        endianness_handling(1.23)

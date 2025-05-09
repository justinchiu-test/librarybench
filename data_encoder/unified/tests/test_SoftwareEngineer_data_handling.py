import sys
import struct
import json
import pytest

from data_handling import (
    handle_endianness,
    encode_nested,
    version_schema,
    add_metadata
)

def test_handle_endianness_int_big():
    # Test integer conversion to big-endian
    num = 0x010203
    be = handle_endianness(num, 'big')
    assert isinstance(be, bytes)
    assert be == b'\x01\x02\x03'

def test_handle_endianness_int_little():
    num = 0x010203
    le = handle_endianness(num, 'little')
    assert isinstance(le, bytes)
    # little-endian of 0x010203 is 03 02 01
    assert le == b'\x03\x02\x01'

def test_handle_endianness_bytes_big_and_little():
    data = b'\xAA\xBB\xCC'
    # Simulate conversions
    be = handle_endianness(data, 'big')
    le = handle_endianness(data, 'little')
    if sys.byteorder == 'big':
        assert be == data
        assert le == data[::-1]
    else:
        assert le == data
        assert be == data[::-1]

def test_handle_endianness_invalid_format():
    with pytest.raises(ValueError):
        handle_endianness(123, 'middle')

def test_handle_endianness_invalid_type():
    with pytest.raises(TypeError):
        handle_endianness(3.14, 'big')

def test_encode_nested_simple():
    schema = {'a': 'uint16', 'b': 'string'}
    data = {'a': 258, 'b': 'hi'}
    result = encode_nested(data, schema)
    # a = 258 => 0x0102, string length 2 + 'hi'
    expected = b'\x01\x02' + struct.pack('!I', 2) + b'hi'
    assert result == expected

def test_encode_nested_multiple_types():
    schema = {
        'x': 'int8',
        'y': 'uint32',
        'msg': 'string'
    }
    data = {'x': -5, 'y': 65537, 'msg': 'ok'}
    result = encode_nested(data, schema)
    expected = struct.pack('!bI', -5, 65537) + struct.pack('!I', 2) + b'ok'
    assert result == expected

def test_encode_nested_nested_schema():
    schema = {
        'outer': {
            'inner1': 'uint8',
            'inner2': 'string'
        },
        'val': 'uint32'
    }
    data = {
        'outer': {'inner1': 10, 'inner2': 'go'},
        'val': 0xAABBCCDD
    }
    part1 = struct.pack('!B', 10) + struct.pack('!I', 2) + b'go'
    part2 = struct.pack('!I', 0xAABBCCDD)
    assert encode_nested(data, schema) == part1 + part2

def test_encode_nested_missing_key():
    schema = {'a': 'uint8', 'b': 'string'}
    data = {'a': 1}
    with pytest.raises(KeyError):
        encode_nested(data, schema)

def test_encode_nested_extra_key():
    schema = {'a': 'uint8'}
    data = {'a': 1, 'b': 2}
    with pytest.raises(ValueError):
        encode_nested(data, schema)

def test_encode_nested_bad_type():
    schema = {'a': 'float32'}
    data = {'a': 1.23}
    with pytest.raises(ValueError):
        encode_nested(data, schema)

def test_version_schema_immutable_original():
    orig = {'a': 'uint8'}
    vs = version_schema(orig, 'v1')
    assert vs['version'] == 'v1'
    assert vs['schema'] == orig
    # Modifying returned schema should not affect original
    vs['schema']['a'] = 'uint16'
    assert orig['a'] == 'uint8'

def test_add_metadata_basic():
    payload = b'PAYLOAD'
    meta = {'author': 'tester', 'id': 123}
    result = add_metadata(payload, meta)
    # first 4 bytes = length of JSON
    length = struct.unpack('!I', result[:4])[0]
    json_bytes = result[4:4+length]
    decoded = json.loads(json_bytes.decode('utf-8'))
    assert decoded == meta
    assert result[4+length:] == payload

def test_add_metadata_empty():
    payload = b''
    meta = {}
    result = add_metadata(payload, meta)
    length = struct.unpack('!I', result[:4])[0]
    assert length == len(b'{}')
    assert json.loads(result[4:4+length].decode()) == {}
    assert result[4+length:] == b''

def test_add_metadata_invalid_data():
    with pytest.raises(TypeError):
        add_metadata("notbytes", {})

def test_add_metadata_invalid_meta():
    with pytest.raises(TypeError):
        add_metadata(b'data', "notdict")

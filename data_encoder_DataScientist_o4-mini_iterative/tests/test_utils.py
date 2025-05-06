import json
import zlib
import pytest

from data_handler import encode_data, decode_data, compress_data

def test_encode_success():
    schema = {'a': int, 'b': str}
    data = {'a': 1, 'b': 'hello', 'extra': 42}
    result = encode_data(data, schema)
    # Should produce valid JSON corresponding to only a and b
    obj = json.loads(result)
    assert obj == {'a': 1, 'b': 'hello'}

def test_encode_missing_key():
    schema = {'x': int, 'y': str}
    data = {'x': 5}
    with pytest.raises(KeyError) as exc:
        encode_data(data, schema)
    assert "Missing key: y" in str(exc.value)

def test_encode_wrong_type():
    schema = {'num': int}
    data = {'num': 'not an int'}
    with pytest.raises(TypeError) as exc:
        encode_data(data, schema)
    assert "expected type int" in str(exc.value)

def test_decode_success():
    schema = {'p': float, 'q': list}
    data = {'p': 3.14, 'q': [1, 2, 3], 'extra': 0}
    encoded = json.dumps({'p': 3.14, 'q': [1, 2, 3]})
    result = decode_data(encoded, schema)
    assert result == {'p': 3.14, 'q': [1, 2, 3]}

def test_decode_invalid_json():
    schema = {'a': int}
    with pytest.raises(ValueError) as exc:
        decode_data("not a json", schema)
    assert "Invalid encoded data" in str(exc.value)

def test_decode_missing_key():
    schema = {'a': int, 'b': str}
    encoded = json.dumps({'a': 10})
    with pytest.raises(KeyError) as exc:
        decode_data(encoded, schema)
    assert "Missing key: b" in str(exc.value)

def test_decode_wrong_type():
    schema = {'a': int}
    encoded = json.dumps({'a': 'oops'})
    with pytest.raises(TypeError) as exc:
        decode_data(encoded, schema)
    assert "expected type int" in str(exc.value)

def test_compress_and_decompress_str():
    original = "hello world"
    compressed = compress_data(original)
    assert isinstance(compressed, bytes)
    decompressed = zlib.decompress(compressed).decode('utf-8')
    assert decompressed == original

def test_compress_and_decompress_bytes():
    original = b"\x00\x01\x02\x03"
    compressed = compress_data(original)
    assert isinstance(compressed, bytes)
    decompressed = zlib.decompress(compressed)
    assert decompressed == original

def test_compress_serializable_object():
    original = {'x': 1, 'y': [2, 3]}
    compressed = compress_data(original)
    assert isinstance(compressed, bytes)
    decompressed = zlib.decompress(compressed).decode('utf-8')
    obj = json.loads(decompressed)
    assert obj == original

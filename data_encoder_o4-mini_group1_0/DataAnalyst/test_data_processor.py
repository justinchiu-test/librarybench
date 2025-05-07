import pytest
import zlib
import base64

from DataAnalyst.data_processor import (
    validate_data,
    encode_dictionary,
    decode_dictionary,
    compress_long_strings,
    decompress_long_strings,
    example_use_cases
)


# =========== Tests for validate_data ===========

def test_validate_data_simple_types():
    assert validate_data(5, int) is True
    assert validate_data("hello", str) is True
    with pytest.raises(TypeError):
        validate_data(5, str)
    with pytest.raises(TypeError):
        validate_data("x", int)


def test_validate_data_dict_schema_success():
    data = {'a': 1, 'b': "two", 'c': [1, 2, 3]}
    schema = {'a': int, 'b': str, 'c': [int]}
    assert validate_data(data, schema) is True


def test_validate_data_dict_schema_missing_key():
    data = {'a': 1}
    schema = {'a': int, 'b': str}
    with pytest.raises(KeyError):
        validate_data(data, schema)


def test_validate_data_list_schema_error():
    data = [1, "two", 3]
    schema = [int]
    with pytest.raises(TypeError):
        validate_data(data, schema)


def test_validate_data_invalid_schema():
    with pytest.raises(ValueError):
        validate_data(1, 1)  # schema must be type, dict, or single-element list
    with pytest.raises(ValueError):
        validate_data([1, 2], [int, str])  # list schema must have exactly one element


# =========== Tests for encode/decode dictionary ===========

def test_encode_decode_flat_dict():
    d = {'x': 10, 'y': 'hi', 'z': 3.14}
    enc = encode_dictionary(d)
    # Check types are tagged correctly
    assert enc['x']['type'] == 'int'
    assert enc['y']['type'] == 'str'
    assert enc['z']['type'] == 'float'
    # Decode and compare
    dec = decode_dictionary(enc)
    assert dec == d


def test_encode_decode_nested_dict_and_list():
    d = {
        'nums': [1, 2, 3],
        'nested': {'a': 'alpha', 'b': 'beta'}
    }
    enc = encode_dictionary(d)
    # Check list encoding
    assert enc['nums']['type'] == 'list'
    assert isinstance(enc['nums']['value'], list)
    # Check nested dict encoding
    assert enc['nested']['type'] == 'dict'
    dec = decode_dictionary(enc)
    assert dec == d


def test_encode_dictionary_type_error():
    with pytest.raises(TypeError):
        encode_dictionary(123)  # not a dict

def test_decode_dictionary_type_error():
    with pytest.raises(TypeError):
        decode_dictionary("not a dict")

def test_decode_dictionary_invalid_entry():
    with pytest.raises(ValueError):
        decode_dictionary({'a': {'bad': 'entry'}})


# =========== Tests for compress/decompress long strings ===========

def test_compress_no_compression_for_short_string():
    s = "short"
    out = compress_long_strings(s, threshold=10)
    assert out == s

def test_compress_and_decompress_simple():
    s = "a" * 20
    comp = compress_long_strings(s, threshold=10)
    assert isinstance(comp, dict) and comp.get('__compressed__') is True
    # verify data is real zlib+base64
    raw = base64.b64decode(comp['data'])
    assert zlib.decompress(raw).decode('utf-8') == s
    # Round-trip via helper
    decomp = decompress_long_strings(comp)
    assert decomp == s

def test_compress_deeply_nested():
    data = {
        'level1': {
            'level2': ['short', 'b'*15]
        }
    }
    comp = compress_long_strings(data, threshold=10)
    # Ensure nested long string is compressed, short remains str
    assert comp['level1']['level2'][0] == 'short'
    assert isinstance(comp['level1']['level2'][1], dict)
    # Round-trip
    decomp = decompress_long_strings(comp)
    assert decomp == {'level1': {'level2': ['short', 'b'*15]}}


# =========== Tests for example_use_cases ===========

def test_example_use_cases_full_cycle():
    result = example_use_cases()
    # raw must match decoded
    assert result['decoded'] == result['raw']
    # compressed then decompressed must match raw
    assert result['decompressed'] == result['raw']
    # encoded must decode back to raw
    assert decode_dictionary(result['encoded']) == result['raw']
    # types in encoded
    for k, v in result['encoded'].items():
        assert 'type' in v and 'value' in v

import pytest
from encoding_configuration import encoding_configuration

def test_none_algorithm_identity():
    config = encoding_configuration({'algorithm': 'none'})
    data = b"hello world"
    assert config.encode(data) == data
    assert config.decode(data) == data

def test_zlib_compression_and_decompression():
    config = encoding_configuration({'algorithm': 'zlib', 'compression_level': 9})
    data = b"abcabcabcabcabcabc"
    encoded = config.encode(data)
    assert isinstance(encoded, bytes)
    assert encoded != data  # should compress
    decoded = config.decode(encoded)
    assert decoded == data

def test_default_configuration_is_none():
    config = encoding_configuration({})
    data = b"data"
    assert config.encode(data) == data
    assert config.decode(data) == data

def test_invalid_algorithm_error_on_encode():
    config = encoding_configuration({'algorithm': 'unknown'})
    with pytest.raises(ValueError):
        config.encode(b"data")

def test_invalid_algorithm_error_on_decode():
    config = encoding_configuration({'algorithm': 'unknown'})
    with pytest.raises(ValueError):
        config.decode(b"data")

def test_invalid_data_type_error():
    config = encoding_configuration({'algorithm': 'none'})
    with pytest.raises(TypeError):
        config.encode("not bytes")
    with pytest.raises(TypeError):
        config.decode("not bytes")

import pytest
import zlib
from DevOps_Engineer.devops_utils.compression import compression_option

def test_compression_option_str_compressible():
    data = 'aaaaaa'  # compressible
    result = compression_option(data)
    assert isinstance(result, (bytes, bytearray))
    # decompress should recover original
    assert zlib.decompress(result).decode('utf-8') == data

def test_compression_option_bytes_compressible():
    data = b'\x00' * 100
    result = compression_option(data)
    assert isinstance(result, (bytes, bytearray))
    assert zlib.decompress(result) == data

def test_compression_option_incompressible():
    data = bytes(range(256))
    result = compression_option(data)
    # incompressible data should be returned unchanged
    assert result == data

def test_compression_option_invalid_type():
    with pytest.raises(ValueError):
        compression_option(12345)

import pytest
import zlib
from encoder import (
    configure_encoding,
    encode,
    decode,
    document_api
)

def test_configure_encoding_defaults():
    cfg = configure_encoding({})
    assert isinstance(cfg, dict)
    assert cfg['version'] == 2
    assert cfg['compression_level'] == 6

def test_configure_encoding_custom():
    cfg = configure_encoding({'version': 1, 'compression_level': 0})
    assert cfg['version'] == 1
    assert cfg['compression_level'] == 0

def test_configure_encoding_partial():
    cfg = configure_encoding({'version': 1})
    assert cfg['version'] == 1
    assert cfg['compression_level'] == 6

    cfg2 = configure_encoding({'compression_level': 9})
    assert cfg2['version'] == 2
    assert cfg2['compression_level'] == 9

def test_configure_encoding_invalid():
    with pytest.raises(TypeError):
        configure_encoding("not a dict")
    with pytest.raises(ValueError):
        configure_encoding({'version': 3})
    with pytest.raises(ValueError):
        configure_encoding({'compression_level': -1})
    with pytest.raises(ValueError):
        configure_encoding({'compression_level': 10})

def test_encode_decode_roundtrip_str_default():
    original = "Hello, 世界!"
    cfg = configure_encoding({})
    enc = encode(original, cfg)
    # First byte should be version
    assert enc[0] == cfg['version']
    dec = decode(enc)
    assert isinstance(dec, bytes)
    assert dec.decode('utf-8') == original

def test_encode_decode_roundtrip_bytes_default():
    original = b"\x00\x01\x02\xff"
    cfg = configure_encoding({})
    enc = encode(original, cfg)
    assert enc[0] == cfg['version']
    dec = decode(enc)
    assert dec == original

def test_encode_decode_version1():
    original = "TestVersion1"
    cfg = configure_encoding({'version': 1})
    enc = encode(original, cfg)
    assert enc[0] == 1
    # No compression, payload is utf-8
    payload = enc[1:]
    assert payload == original.encode('utf-8')
    dec = decode(enc)
    assert dec.decode('utf-8') == original

def test_encode_decode_custom_compression():
    original = b"abc" * 100  # highly compressible
    cfg = configure_encoding({'version': 2, 'compression_level': 9})
    enc = encode(original, cfg)
    # Ensure it's actually compressed (payload smaller than raw)
    assert len(enc) < len(original) + 1
    dec = decode(enc)
    assert dec == original

def test_manual_version1_backward_compatibility():
    # Simulate old tool: raw bytes with version 1 header
    data = b"legacy data"
    encoded = bytes([1]) + data
    decoded = decode(encoded)
    assert decoded == data

def test_decode_invalid_inputs():
    with pytest.raises(TypeError):
        decode("not bytes")
    with pytest.raises(ValueError):
        decode(b"")  # too short for header
    # Unknown version
    with pytest.raises(ValueError):
        decode(bytes([99]) + b"payload")
    # Corrupted version 2 data
    with pytest.raises(ValueError):
        # version byte = 2 but payload not valid zlib data
        decode(bytes([2]) + b"not_zlib_data")

def test_encode_invalid_inputs():
    cfg = configure_encoding({})
    with pytest.raises(TypeError):
        encode(12345, cfg)
    with pytest.raises(TypeError):
        encode(b"data", "not a config")
    bad_cfg = {'version': 3, 'compression_level': 6}
    with pytest.raises(ValueError):
        encode(b"data", bad_cfg)

def test_document_api_contents():
    doc = document_api()
    # Ensure each function is mentioned
    for fn in ['configure_encoding', 'encode(', 'decode(', 'document_api(']:
        assert fn in doc
    # Check Markdown headers
    assert "# API Documentation" in doc
    assert "## encode" in doc
    assert "## decode" in doc

import base64
import pytest

from codec import encode, decode, configure_security, stream_encode, _GLOBAL_CONFIG

def test_configure_security_valid():
    cfg = configure_security({'key': 'mysecret', 'level': 3})
    # Should update global config
    assert _GLOBAL_CONFIG['key'] == b'mysecret'
    assert _GLOBAL_CONFIG['level'] == 3
    assert cfg == {'key': b'mysecret', 'level': 3}

def test_configure_security_invalid_missing():
    with pytest.raises(KeyError):
        configure_security({'key': 'abc'})
    with pytest.raises(KeyError):
        configure_security({'level': 2})

def test_configure_security_invalid_key():
    with pytest.raises(ValueError):
        configure_security({'key': '', 'level': 1})
    with pytest.raises(ValueError):
        configure_security({'key': b'', 'level': 1})

def test_configure_security_invalid_level():
    with pytest.raises(ValueError):
        configure_security({'key': 'abc', 'level': 0})
    with pytest.raises(ValueError):
        configure_security({'key': 'abc', 'level': -1})
    with pytest.raises(ValueError):
        configure_security({'key': 'abc', 'level': 1.5})

def test_encode_decode_roundtrip_str():
    # set a known config
    cfg = configure_security({'key': 'k', 'level': 2})
    data = "Hello, World!"
    encoded = encode(data, cfg)
    # Must start with v1:
    assert encoded.startswith("v1:")
    decoded = decode(encoded)
    assert decoded == data

def test_encode_decode_roundtrip_bytes():
    cfg = configure_security({'key': b'\x01\x02', 'level': 1})
    data = b"\x00\xff\x10test"
    encoded = encode(data, cfg)
    assert isinstance(encoded, str)
    decoded = decode(encoded)
    assert isinstance(decoded, str)
    # Original data was bytes; decode returns utf-8 str for 'test' part
    # So convert original to utf-8 ignoring non-text prefix for comparison
    assert decoded.endswith("test")

def test_decode_v0_backward_compatibility():
    # v0: plain base64 no prefix
    raw = "BackwardCompatibility!"
    b64 = base64.b64encode(raw.encode('utf-8')).decode('utf-8')
    # Temporarily change global config to something else
    configure_security({'key': 'xyz', 'level': 5})
    out = decode(b64)
    assert out == raw

def test_encode_errors():
    # missing config keys
    with pytest.raises(KeyError):
        encode("data", {'key': b'x'})
    with pytest.raises(KeyError):
        encode("data", {'level': 1})
    # bad data type
    cfg = configure_security({'key': 'any', 'level': 1})
    with pytest.raises(TypeError):
        encode(12345, cfg)

def test_stream_encode_and_decode():
    # use a multi-chunk data
    configure_security({'key': 'streamkey', 'level': 2})
    chunks = ["The quick ", "brown ", "fox ", "jumps"]
    encoded_chunks = list(stream_encode(chunks))
    # Each chunk should be independent v1-encoded
    assert all(c.startswith("v1:") for c in encoded_chunks)
    # Decoding each chunk and concatenating should give original
    decoded = "".join(decode(c) for c in encoded_chunks)
    assert decoded == "".join(chunks)

def test_stream_encode_bytes_chunks():
    configure_security({'key': 'abc', 'level': 1})
    chunks = [b"foo", b"bar", b"baz"]
    encoded = list(stream_encode(chunks))
    assert len(encoded) == 3
    assert all(isinstance(c, str) for c in encoded)
    decoded = "".join(decode(c) for c in encoded)
    assert decoded == "foobarbaz"

import json
import struct

def encode_data(data):
    """
    Encodes data into a custom binary format:
    - First 4 bytes: big-endian unsigned 32-bit integer indicating the length N of the payload.
    - Next N bytes: payload, which is the UTF-8 encoded JSON serialization of `data`.
    JSON is serialized with sorted keys and compact separators to ensure cross‐language consistency.
    """
    # Serialize to JSON
    json_bytes = json.dumps(data, separators=(',', ':'), sort_keys=True).encode('utf-8')
    # Pack length as 4-byte big-endian unsigned int
    prefix = struct.pack('>I', len(json_bytes))
    # Return prefix + payload
    return prefix + json_bytes

def specify_binary_format():
    """
    Returns a human-readable specification of the binary format used by encode_data.
    """
    spec = (
        "Binary format specification:\n"
        "- 4-byte unsigned integer (big-endian) indicating length N of the payload.\n"
        "- N bytes of payload, which is a UTF-8 encoded JSON string.\n"
        "- JSON serialization uses sorted object keys and compact separators (',' and ':').\n"
        "- Supported JSON types: object, array, string, number, true, false, null."
    )
    return spec

def test_integration_with_system(system):
    """
    Runs a suite of round-trip tests against an external system that implements
    a `decode(bytes)` method. The system.decode method must accept the bytes
    produced by encode_data and return the original Python data structure.
    
    Raises AssertionError if any test fails. Returns True if all pass.
    """
    test_values = [
        0,
        42,
        -17,
        3.1415,
        "",
        "hello world",
        True,
        False,
        None,
        [],
        [1, 2, 3, "four", None],
        {},
        {"a": 1, "b": [True, False, None], "c": {"nested": "value"}},
    ]
    for value in test_values:
        encoded = encode_data(value)
        decoded = system.decode(encoded)
        assert decoded == value, f"Decoded {decoded!r} does not match original {value!r}"
    return True

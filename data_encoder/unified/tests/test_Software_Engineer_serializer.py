import json
import struct
import pytest
import serializer

class DummySystem:
    """
    A dummy system that knows how to decode the binary format defined in serializer.py.
    """
    def decode(self, data_bytes):
        # Must be at least 4 bytes for the length prefix
        if len(data_bytes) < 4:
            raise ValueError("Data too short to contain length prefix")
        # Unpack length
        length = struct.unpack('>I', data_bytes[:4])[0]
        payload = data_bytes[4:]
        if len(payload) != length:
            raise ValueError(f"Payload length mismatch: expected {length}, got {len(payload)}")
        # Decode JSON payload
        return json.loads(payload.decode('utf-8'))

def test_encode_data_prefix_and_payload():
    # Prepare a sample dict with keys out of order to test sort_keys
    data = {"z": "last", "a": "first"}
    encoded = serializer.encode_data(data)
    # Should be bytes and at least 4 bytes long
    assert isinstance(encoded, (bytes, bytearray))
    assert len(encoded) >= 4

    # Check the 4-byte prefix correctly represents the payload length
    length_prefix = struct.unpack('>I', encoded[:4])[0]
    payload = encoded[4:]
    assert length_prefix == len(payload)

    # Payload should be valid JSON that matches the original data
    decoded_payload = json.loads(payload.decode('utf-8'))
    assert decoded_payload == data

def test_specify_binary_format_content():
    spec = serializer.specify_binary_format()
    # Check that key terms appear in the specification
    assert "4-byte" in spec
    assert "big-endian" in spec
    assert "UTF-8" in spec
    assert "JSON" in spec
    assert "length N" in spec

def test_integration_with_dummy_system():
    dummy = DummySystem()
    # Should complete all round-trip tests and return True
    assert serializer.test_integration_with_system(dummy) is True

def test_integration_with_bad_system():
    class BadSystem:
        # Always returns incorrect data
        def decode(self, data_bytes):
            return "wrong"

    bad = BadSystem()
    # Integration test should raise AssertionError on mismatch
    with pytest.raises(AssertionError):
        serializer.test_integration_with_system(bad)

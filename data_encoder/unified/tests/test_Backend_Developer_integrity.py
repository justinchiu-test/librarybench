import pytest
from nested_codec import encode_nested_structures, check_data_integrity

def test_integrity_identical_encodings_are_stable():
    data = {"a": 1, "b": [2,3]}
    enc1 = encode_nested_structures(data)
    enc2 = encode_nested_structures(data)
    assert enc1 == enc2
    assert check_data_integrity(enc1)

def test_tamper_checksum_field():
    # Manually craft a bad checksum
    good = encode_nested_structures({"x":10})
    text = good.decode()
    obj = __import__('json').loads(text)
    obj["checksum"] = "0"*64
    bad = __import__('json').dumps(obj, sort_keys=True, separators=(",",":")).encode()
    assert not check_data_integrity(bad)

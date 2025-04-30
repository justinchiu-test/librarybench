import pytest
import json
import zlib

from data_pipeline import (
    DataPipeline,
    data_integrity_checks,
    nested_structures,
    streaming_support,
    encoding_configuration,
)


def test_encode_decode_no_compression_basic_types():
    dp = DataPipeline()
    data = {"int": 1, "str": "hello", "list": [1, 2, 3], "dict": {"a": True}}
    encoded = dp.encode(data)
    # Should be raw JSON bytes
    assert isinstance(encoded, bytes)
    decoded = dp.decode(encoded)
    assert decoded == data


def test_data_integrity_checks_round_trip():
    complex_data = {
        "nested": {"x": [1, {"y": 2}, [3, [4, {"z": "end"}]]]},
        "empty": [],
        "none": None,
    }
    assert data_integrity_checks(complex_data) is True


def test_nested_structures_preserved():
    nested = {"a": [{"b": [1, 2, {"c": 3}]}], "d": {"e": {"f": []}}}
    result = nested_structures(nested)
    assert result == nested


def test_compression_levels_shrink_size_and_preserve_data():
    data = {"text": "a" * 1000, "numbers": list(range(100))}
    dp1 = DataPipeline(compression_level=1)
    dp9 = DataPipeline(compression_level=9)
    enc1 = dp1.encode(data)
    enc9 = dp9.encode(data)
    # High compression should not produce larger output
    assert len(enc9) <= len(enc1)
    # Both decode back correctly
    assert dp1.decode(enc1) == data
    assert dp9.decode(enc9) == data


def test_invalid_compression_level_raises():
    with pytest.raises(ValueError):
        DataPipeline(compression_level=-1)
    with pytest.raises(ValueError):
        DataPipeline(compression_level=10)
    with pytest.raises(ValueError):
        DataPipeline(compression_level="high")


def test_encoding_configuration_returns_pipeline():
    cfg = {"compression_level": 5}
    dp = encoding_configuration(cfg)
    assert isinstance(dp, DataPipeline)
    assert dp.compression_level == 5

    # Missing key uses default
    dp2 = encoding_configuration({})
    assert dp2.compression_level == 0

    # Non-dict settings
    with pytest.raises(ValueError):
        encoding_configuration(["not", "a", "dict"])


def test_encode_invalid_data_type():
    dp = DataPipeline()
    # set is not JSON serializable
    with pytest.raises(ValueError):
        dp.encode({ "a": set([1, 2]) })


def test_decode_invalid_bytes():
    dp = DataPipeline()
    # Not valid JSON
    with pytest.raises(ValueError):
        dp.decode(b'{"a":1')  # incomplete
    # Not bytes
    with pytest.raises(ValueError):
        dp.decode("not-bytes")


def test_streaming_support_encode_and_decode():
    items = [{"x": i} for i in range(5)]
    encoded_chunks = list(streaming_support(items))
    assert len(encoded_chunks) == 5
    # Each chunk must decode back to its original item
    dp = DataPipeline()
    decoded = [dp.decode(chunk) for chunk in encoded_chunks]
    assert decoded == items

def test_streaming_support_independence():
    # Ensure streaming_support always uses fresh default pipeline
    items = [{"foo": "bar"}]
    chunks1 = list(streaming_support(items))
    # If you compress by manually using a non-default pipeline, pipeline inside streaming
    # should still be default (i.e., no compression)
    # First chunk should be raw JSON, not zlib-compressed
    raw = chunks1[0]
    # raw JSON should start with b'{' and not match a zlib header
    assert raw.startswith(b"{")
    assert not raw.startswith(b"\x78")  # common zlib magic byte

def test_checksum_stable_for_same_data():
    # As an extra integrity check, identical data produce same encoding w/o compression
    dp = DataPipeline()
    d1 = {"a": 1, "b": 2}
    d2 = {"b": 2, "a": 1}  # same data, different insertion order
    e1 = dp.encode(d1)
    e2 = dp.encode(d2)
    assert e1 == e2  # because we sort_keys=True

def test_compressed_data_not_plain_json():
    dp = DataPipeline(compression_level=6)
    data = {"a": 1}
    compressed = dp.encode(data)
    # compressed data should not be valid JSON directly
    with pytest.raises(json.JSONDecodeError):
        json.loads(compressed.decode('utf-8'))
    # but dp.decode should succeed
    assert dp.decode(compressed) == data

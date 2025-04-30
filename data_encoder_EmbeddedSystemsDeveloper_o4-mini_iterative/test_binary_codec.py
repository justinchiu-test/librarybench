import struct
import pytest

from binary_codec import (
    encode_binary,
    decode_binary,
    handle_nested_structures,
    error_handling_process,
    BinaryCodecError,
)


def test_encode_decode_flat_structure():
    schema = [
        ("f1", ">H"),   # big-endian unsigned short
        ("f2", "<I"),   # little-endian unsigned int
        ("f3", "B"),    # unsigned char
    ]
    data = {"f1": 0x1234, "f2": 0xAABBCCDD, "f3": 255}
    expected = struct.pack(">H", data["f1"]) + struct.pack("<I", data["f2"]) + struct.pack("B", data["f3"])
    encoded = encode_binary(data, schema)
    assert isinstance(encoded, (bytes, bytearray))
    assert encoded == expected

    decoded = decode_binary(encoded, schema)
    assert decoded == data


def test_encode_decode_nested_structure():
    schema = [
        ("hdr", ">H"),
        ("body", [
            ("a", "B"),
            ("b", "<I"),
        ]),
        ("ftr", ">H"),
    ]
    data = {
        "hdr": 1,
        "body": {"a": 2, "b": 0xDEADBEEF},
        "ftr": 3,
    }
    # manual pack
    manual = struct.pack(">H", 1) + struct.pack("B", 2) + struct.pack("<I", 0xDEADBEEF) + struct.pack(">H", 3)
    enc = encode_binary(data, schema)
    assert enc == manual
    dec = decode_binary(enc, schema)
    assert dec == data


def test_missing_key_raises_error():
    schema = [("x", "B"), ("y", "B")]
    data = {"x": 10}
    with pytest.raises(BinaryCodecError) as exc:
        encode_binary(data, schema)
    assert "Missing key 'y'" in str(exc.value)


def test_incorrect_type_raises_error():
    schema = [("x", "B")]
    data = {"x": "not_an_int"}
    with pytest.raises(BinaryCodecError) as exc:
        encode_binary(data, schema)
    assert "Error packing field 'x'" in str(exc.value)


def test_decode_insufficient_bytes():
    schema = [("x", "I"), ("y", "I")]
    # only 4 bytes provided, but need 8
    bad_bytes = struct.pack("I", 100)
    with pytest.raises(BinaryCodecError) as exc:
        decode_binary(bad_bytes, schema)
    assert "Not enough bytes to unpack field 'y'" in str(exc.value)


def test_handle_nested_structures_flattening():
    nested = {
        "a": 1,
        "b": {"c": 2, "d": {"e": 3}},
        "f": 4
    }
    flat = handle_nested_structures(nested)
    expected = {
        "a": 1,
        "b.c": 2,
        "b.d.e": 3,
        "f": 4
    }
    assert flat == expected


def test_error_handling_process_success():
    schema = [("x", "B")]
    data = {"x": 5}
    ok, result = error_handling_process(encode_binary, data, schema)
    assert ok is True
    assert isinstance(result, (bytes, bytearray))
    # also after decode
    ok2, dec = error_handling_process(decode_binary, result, schema)
    assert ok2 and dec == data


def test_error_handling_process_failure():
    schema = [("x", "B")]
    data = {"x": "bad"}
    ok, err_msg = error_handling_process(encode_binary, data, schema)
    assert ok is False
    assert "Error packing field 'x'" in err_msg

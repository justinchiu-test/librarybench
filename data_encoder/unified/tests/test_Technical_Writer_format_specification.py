import pytest
from format_spec import generate_format_specification


def test_generate_specification_empty():
    # An empty format yields only the header and table skeleton
    fmt = {}
    expected = (
        "# Binary Format Specification\n"
        "\n"
        "Field | Type | Size (bytes) | Description\n"
        "--- | --- | --- | ---"
    )
    assert generate_format_specification(fmt) == expected


def test_generate_specification_single_field():
    fmt = {
        "magic": {
            "type": "uint32",
            "size": 4,
            "description": "Magic number to identify file format"
        }
    }
    expected = (
        "# Binary Format Specification\n"
        "\n"
        "Field | Type | Size (bytes) | Description\n"
        "--- | --- | --- | ---\n"
        "magic | uint32 | 4 | Magic number to identify file format"
    )
    result = generate_format_specification(fmt)
    assert result == expected


def test_generate_specification_multiple_fields_and_order():
    # Ensure order is preserved as insertion order in dict
    fmt = {
        "header": {
            "type": "bytes",
            "size": 8,
            "description": "File identifier"
        },
        "version": {
            "type": "uint8",
            "size": 1,
            "description": "Format version"
        },
        "flags": {
            "type": "uint8",
            "size": 1,
            "description": "Bit-flags for options"
        },
        "payload": {
            "type": "bytes",
            "size": "remaining",
            "description": "Payload data"
        },
    }
    result = generate_format_specification(fmt)
    lines = result.splitlines()
    # Check header
    assert lines[0] == "# Binary Format Specification"
    assert lines[2].startswith("Field | Type | Size")
    # Check each field line in order
    assert lines[4] == "header | bytes | 8 | File identifier"
    assert lines[5] == "version | uint8 | 1 | Format version"
    assert lines[6] == "flags | uint8 | 1 | Bit-flags for options"
    assert lines[7] == "payload | bytes | remaining | Payload data"


@pytest.mark.parametrize("bad_input", [
    None,
    123,
    "not a dict",
    [("a", {"type": "uint8", "size": 1, "description": "desc"})]
])
def test_invalid_format_type(bad_input):
    with pytest.raises(TypeError):
        generate_format_specification(bad_input)


def test_invalid_field_name_type():
    fmt = {
        123: {"type": "uint8", "size": 1, "description": "desc"}
    }
    with pytest.raises(TypeError):
        generate_format_specification(fmt)


@pytest.mark.parametrize("spec", [
    None,
    "not a dict",
    123,
    ["list"]
])
def test_invalid_spec_type(spec):
    fmt = {"field": spec}
    with pytest.raises(TypeError):
        generate_format_specification(fmt)


def test_missing_or_invalid_type_key():
    fmt1 = {"field": {"size": 2, "description": "desc"}}
    fmt2 = {"field": {"type": 5, "size": 2, "description": "desc"}}
    with pytest.raises(TypeError):
        generate_format_specification(fmt1)
    with pytest.raises(TypeError):
        generate_format_specification(fmt2)


def test_missing_or_invalid_size_key():
    fmt1 = {"field": {"type": "uint16", "description": "desc"}}
    fmt2 = {"field": {"type": "uint16", "size": 2.5, "description": "desc"}}
    with pytest.raises(TypeError):
        generate_format_specification(fmt1)
    with pytest.raises(TypeError):
        generate_format_specification(fmt2)


def test_missing_or_invalid_description_key():
    fmt1 = {"field": {"type": "uint16", "size": 2}}
    fmt2 = {"field": {"type": "uint16", "size": 2, "description": 42}}
    with pytest.raises(TypeError):
        generate_format_specification(fmt1)
    with pytest.raises(TypeError):
        generate_format_specification(fmt2)

import pytest
from config_framework.custom_coercers import parse_bytes

def test_parse_bytes_no_unit():
    assert parse_bytes("1024") == 1024

def test_parse_bytes_kb():
    assert parse_bytes("1kb") == 1024
    assert parse_bytes("1K") == 1024

def test_parse_bytes_mb():
    assert parse_bytes("0.5MB") == int(0.5 * 1024**2)

def test_invalid():
    with pytest.raises(ValueError):
        parse_bytes("abc")
    with pytest.raises(ValueError):
        parse_bytes("10XB")

import pytest
from validate_schema import validate_schema

def test_validate_with_dict():
    msg = {'price': 10, 'volume': 5, 'symbol': 'ABC'}
    assert validate_schema(msg) == msg

def test_validate_with_json_string():
    s = '{"price": 1, "volume": 2, "symbol": "XYZ"}'
    assert validate_schema(s) == {"price": 1, "volume": 2, "symbol": "XYZ"}

def test_validate_missing_field():
    with pytest.raises(ValueError):
        validate_schema({'price':1, 'volume':2})

import pytest
from pipeline.data_validation import DataValidation

def test_validate_with_rules():
    rules = {
        "age": lambda x: x >= 0,
        "name": lambda x: isinstance(x, str) and len(x) > 0
    }
    dv = DataValidation(rules=rules)
    records = [{"age": 10, "name": "Alice"}, {"age": -5, "name": ""}, {"age": 5}]
    valid, invalid = dv.validate(records)
    assert valid == [{"age": 10, "name": "Alice"}]
    assert len(invalid) == 2

def test_validate_with_schema():
    schema = {"id": int, "value": float}
    dv = DataValidation(schema=schema)
    records = [{"id": 1, "value": 2.5}, {"id": "x", "value": 1.0}, {"id": 2}]
    valid, invalid = dv.validate(records)
    assert valid == [{"id": 1, "value": 2.5}]
    assert len(invalid) == 2

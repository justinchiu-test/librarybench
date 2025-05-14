import pytest
from single_validation import SingleItemValidation

def test_validate_success():
    schema = {'a': {'type': int, 'min': 0, 'max': 10},
              'b': {'type': list, 'length': 2, 'optional': True}}
    rec = {'a': 5, 'b': [1,2]}
    v = SingleItemValidation()
    ok, errors = v.validate(rec, schema)
    assert ok
    assert errors == []

def test_validate_missing_and_invalid_and_outlier_and_length():
    schema = {'a': {'type': int, 'min': 0, 'max': 10},
              'b': {'type': list, 'length': 3}}
    rec = {'a': 20, 'b': [1,2]}
    v = SingleItemValidation()
    ok, errors = v.validate(rec, schema)
    assert not ok
    types = sorted([e['type'] for e in errors])
    assert types == ['length', 'outlier']

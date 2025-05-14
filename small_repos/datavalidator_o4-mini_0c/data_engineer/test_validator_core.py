import pytest
from etl_validator.schema import SchemaDefinition
from etl_validator.validator import Validator

@pytest.fixture
def schema_def():
    return SchemaDefinition({
        'fields': {
            'order_id': {'type': 'string', 'required': True},
            'order_status': {'type': 'string', 'values': ['pending', 'shipped'], 'required': True},
            'shipment_date': {
                'type': 'string',
                'required': False,
                'condition': {'field': 'order_status', 'equals': 'shipped'}
            },
            'quantity': {'type': 'number', 'min': 1, 'max': 100, 'required': True},
            'price': {'type': 'number', 'min': 0.0, 'required': True},
            'latency': {'type': 'number', 'min': 0},
            'comment': {'type': 'string'},
            'discount_reason': {'type': 'string'},
            'timestamp': {'type': 'string', 'default': 'now'},
            'environment': {'type': 'string', 'default': 'prod'}
        },
        'strict': True
    })

def test_missing_required(schema_def):
    val = Validator(schema_def)
    record = {'order_status': 'pending', 'quantity': 10, 'price': 5.0}
    result = val.validate(record)
    assert not result.success
    codes = [e['code'] for e in result.errors]
    assert 'REQUIRED' in codes

def test_enum_violation(schema_def):
    val = Validator(schema_def)
    record = {'order_id': '1', 'order_status': 'invalid', 'quantity': 10, 'price': 5.0}
    result = val.validate(record)
    assert not result.success
    assert any(e['code'] == 'ENUM' for e in result.errors)

def test_conditional_validation(schema_def):
    val = Validator(schema_def)
    # status pending, skip shipment_date
    rec1 = {'order_id': '1', 'order_status': 'pending', 'quantity': 1, 'price': 1.0}
    r1 = val.validate(rec1)
    assert r1.success
    # status shipped, missing shipment_date -> error
    rec2 = {'order_id': '2', 'order_status': 'shipped', 'quantity': 1, 'price': 1.0}
    r2 = val.validate(rec2)
    assert not r2.success
    assert any(e['field'] == 'shipment_date' and e['code'] == 'REQUIRED' for e in r2.errors)

def test_default_values(schema_def):
    val = Validator(schema_def)
    rec = {'order_id': '1', 'order_status': 'pending', 'quantity': 1, 'price': 1.0}
    r = val.validate(rec)
    assert r.success
    assert 'timestamp' in r.record
    assert 'environment' in r.record

def test_range_checks(schema_def):
    val = Validator(schema_def)
    rec = {'order_id': '1', 'order_status': 'pending', 'quantity': 0, 'price': -1.0}
    r = val.validate(rec)
    assert not r.success
    codes = [e['code'] for e in r.errors]
    assert codes.count('RANGE') >= 2

def test_optional_fields_flagged(schema_def):
    val = Validator(schema_def)
    rec = {
        'order_id': '1',
        'order_status': 'pending',
        'quantity': 1,
        'price': 1.0,
        'comment': 'test'
    }
    r = val.validate(rec)
    assert r.success
    assert any(w['code'] == 'OPTIONAL' and w['field'] == 'comment' for w in r.warnings)

def test_strict_mode_extra_field(schema_def):
    val = Validator(schema_def)
    rec = {
        'order_id': '1',
        'order_status': 'pending',
        'quantity': 1,
        'price': 1.0,
        'extra': 'oops'
    }
    r = val.validate(rec)
    assert not r.success
    assert any(e['code'] == 'EXTRA_FIELD' for e in r.errors)

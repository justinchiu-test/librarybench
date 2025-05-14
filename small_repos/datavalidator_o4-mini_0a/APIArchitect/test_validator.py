import pytest
from api_validator.validator import Validator

schema_v1 = {
    'id': {'type': int, 'required': True, 'error_code': 'ID_ERR'},
    'name': {'type': str, 'required': True, 'max_length': 5, 'error_code': 'NAME_ERR'},
    'type': {'type': str, 'required': False, 'default': 'basic', 'error_code': 'TYPE_ERR'},
    'config': {'type': dict, 'required': False, 'error_code': 'CONFIG_ERR'}
}
conditional = [(lambda d: d.get('type') == 'advanced', 'config', 'CONFIG_REQ')]

def test_validate_single_success():
    v = Validator(schema_v1, version=1, conditional_rules=conditional)
    data = {'id': 1, 'name': 'joe'}
    res = v.validate(data)
    assert res['valid']
    assert res['errors'] == []

def test_validate_single_missing_required():
    v = Validator(schema_v1, version=1)
    res = v.validate({'name': 'joe'})
    assert not res['valid']
    assert any(e['field'] == 'id' for e in res['errors'])

def test_validate_single_type_and_length():
    v = Validator(schema_v1, version=1)
    data = {'id': 'x', 'name': 'toolongname'}
    res = v.validate(data)
    fields = {e['field'] for e in res['errors']}
    assert 'id' in fields and 'name' in fields

def test_validate_single_conditional():
    v = Validator(schema_v1, version=1, conditional_rules=conditional)
    data = {'id': 2, 'name': 'ann', 'type': 'advanced'}
    res = v.validate(data)
    assert not res['valid']
    assert any(e['code'] == 'CONFIG_REQ' for e in res['errors'])

def test_validate_batch():
    v = Validator(schema_v1, version=1, conditional_rules=conditional)
    items = [
        {'id': 1, 'name': 'a'},
        {'id': 'no', 'name': 'b'},
        {'id': 3, 'name': 'longname'},
    ]
    report = v.validate(items, batch=True)
    assert report['success'] == 1
    assert report['fail'] == 2
    assert len(report['results']) == 3

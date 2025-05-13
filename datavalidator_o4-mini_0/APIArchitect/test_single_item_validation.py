from api_validator.single_item_validation import SingleItemValidation

def test_validate_item_success():
    siv = SingleItemValidation()
    schema = {'x': {'type': int, 'required': True, 'error_code': 'X_ERR'}}
    data = {'x': 5}
    result = siv.validate_item(data, schema)
    assert result['valid']
    assert result['errors'] == []

def test_validate_item_missing_and_type():
    siv = SingleItemValidation()
    schema = {
        'x': {'type': int, 'required': True, 'error_code': 'X_ERR'},
        'y': {'type': str, 'required': False, 'error_code': 'Y_ERR'}
    }
    data = {'y': 123}
    result = siv.validate_item(data, schema)
    assert not result['valid']
    fields = {e['field'] for e in result['errors']}
    assert 'x' in fields and 'y' in fields

from api_validator.length_constraints import LengthConstraints

def test_validate_length():
    lc = LengthConstraints()
    schema = {'a': {'max_length': 3, 'error_code': 'LEN_ERR'}}
    data = {'a': 'toolong'}
    errors = lc.validate_length(data, schema)
    assert errors and errors[0]['error'] == 'max_length'
    data2 = {'a': 'ok'}
    assert lc.validate_length(data2, schema) == []

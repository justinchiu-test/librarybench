from api_validator.optional_fields import OptionalFields

def test_apply_optional():
    of = OptionalFields()
    schema = {
        'a': {'required': False, 'error_code': 'A_ERR'},
        'b': {'required': True, 'error_code': 'B_ERR', 'error_level': 'warn'}
    }
    data = {}
    errors = of.apply_optional(data, schema)
    assert errors and errors[0]['field'] == 'b'
    assert errors[0]['level'] == 'warn'

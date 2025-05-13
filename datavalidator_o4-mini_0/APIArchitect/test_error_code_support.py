from api_validator.error_code_support import ErrorCodeSupport

def test_assign_code():
    code = ErrorCodeSupport.assign_code('field', 'missing')
    assert code == 'FIELD_MISSING'

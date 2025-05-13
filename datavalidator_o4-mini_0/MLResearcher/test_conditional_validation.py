from conditional_validation import conditional_validate

def test_conditional_skip_and_require():
    schema = {
        'region': {'type': str},
        'rainfall': {'type': float, 'condition': ('region', 'coastal')}
    }
    rec1 = {'region': 'inland'}
    errors1 = conditional_validate(rec1, schema)
    assert errors1 == []
    rec2 = {'region': 'coastal'}
    errors2 = conditional_validate(rec2, schema)
    assert errors2 == [{'field': 'rainfall', 'type': 'missing'}]

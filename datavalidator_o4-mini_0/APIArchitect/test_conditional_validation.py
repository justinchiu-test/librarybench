from api_validator.conditional_validation import ConditionalValidation

def test_apply_conditional():
    cv = ConditionalValidation()
    rule = (lambda d: d.get('flag'), 'must', 'ERR1')
    data = {'flag': True}
    errors = cv.apply_conditional(data, [rule])
    assert errors and errors[0]['field'] == 'must'
    data2 = {'flag': False}
    assert cv.apply_conditional(data2, [rule]) == []

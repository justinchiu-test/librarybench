from datavalidation.conditional_validation import ConditionalValidation

def test_conditional_validation():
    cv = ConditionalValidation()
    def cond(record):
        return [{'field': 'a'}] if record.get('a') != 1 else []
    cv.add_condition('test', cond)
    assert cv.validate({'a': 1}, 'test') == []
    result = cv.validate({'a': 2}, 'test')
    assert result and result[0]['field'] == 'a'

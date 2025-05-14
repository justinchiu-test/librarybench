from batch_validation import BatchValidationInterface

def test_validate_batch():
    schema = {'x': {'type': int}, 'y': {'type': int, 'optional': True}}
    records = [{'x':1, 'y':2}, {'x':None}, {'x':5}]
    bvi = BatchValidationInterface()
    summary = bvi.validate_batch(records, schema)
    assert summary['valid'] == 2
    assert summary['invalid'] == 1
    assert summary['errors']['missing'] == 1

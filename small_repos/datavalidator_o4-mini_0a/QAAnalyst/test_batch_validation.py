from datavalidation.batch_validation import BatchValidationInterface
from datavalidation.single_validation import SingleItemValidation

def test_batch_validation():
    schema = {'required': ['id'], 'optional': []}
    sv = SingleItemValidation(schema)
    batch = BatchValidationInterface(sv)
    records = [{'id':1}, {}]
    summary = batch.validate_batch(records)
    assert summary['total'] == 2
    assert summary['failed'] == 1
    assert len(summary['details']) == 2

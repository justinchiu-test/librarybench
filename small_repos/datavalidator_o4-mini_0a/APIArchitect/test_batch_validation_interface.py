from api_validator.batch_validation_interface import BatchValidationInterface

class Dummy(BatchValidationInterface):
    def validate_single(self, item):
        return {'valid': item % 2 == 0}

def test_validate_batch():
    d = Dummy()
    report = d.validate_batch([1,2,3,4])
    assert report['success'] == 2
    assert report['fail'] == 2
    assert len(report['results']) == 4

from logger_integration import StructuredLogger

def test_logging_integration():
    logger = StructuredLogger()
    payload = {'id': 'x'}
    errors = [{'path': 'id', 'message': 'Expected integer', 'expected': 'integer', 'actual': 'str'}]
    logger.log_validation(payload, errors)
    assert len(logger.records) == 1
    record = logger.records[0]
    assert record['payload'] == payload
    assert record['errors'] == errors

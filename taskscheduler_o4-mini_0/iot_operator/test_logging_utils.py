import logging
from iot_scheduler.logging_utils import attach_log_context

def test_attach_log_context():
    logger = logging.getLogger('test')
    adapter = attach_log_context(logger, job_id='123', device_group='g1')
    msg, extra = adapter.process('hello', {'key': 'value'})
    assert msg == 'hello'
    assert extra['job_id'] == '123'
    assert extra['device_group'] == 'g1'
    assert extra['key'] == 'value'

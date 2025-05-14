import logging
from scheduler.logging import attach_log_context

def test_attach_log_context(caplog):
    caplog.set_level(logging.INFO)
    logger = attach_log_context('job1', 'host1', 'daily')
    logger.info("test message")
    rec = caplog.records[0]
    assert rec.job_id == 'job1'
    assert rec.target_host == 'host1'
    assert rec.schedule_type == 'daily'
    assert rec.getMessage() == 'test message'

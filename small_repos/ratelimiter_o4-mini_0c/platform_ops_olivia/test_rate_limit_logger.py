from ratelimiter.logger import RateLimitLogger

def test_rate_limit_logger_records_denied():
    logger = RateLimitLogger()
    logger.log_denied({'id': 1})
    logger.log_denied('req2')
    assert len(logger.logs) == 2
    assert logger.logs[0]['request'] == {'id': 1}
    assert logger.logs[1]['request'] == 'req2'
    assert all(entry['status'] == 'denied' for entry in logger.logs)

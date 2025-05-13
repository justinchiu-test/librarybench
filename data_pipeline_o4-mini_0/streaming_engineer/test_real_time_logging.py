import sys
import io
from real_time_logging import get_logger

def test_logger_writes_to_stdout(monkeypatch):
    stream = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', stream)
    logger = get_logger('testlogger')
    logger.info('hello world')
    content = stream.getvalue()
    assert 'hello world' in content

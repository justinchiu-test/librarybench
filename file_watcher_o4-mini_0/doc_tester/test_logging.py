import logging
from watcher import LoggingSupport

def test_logging_support(tmp_path):
    log_file = tmp_path / "app.log"
    ls = LoggingSupport(name="testlogger", log_file=str(log_file), level=logging.DEBUG, max_bytes=100, backup_count=1)
    ls.logger.debug("debug message")
    ls.set_level(logging.INFO)
    ls.logger.debug("should not appear")
    content = log_file.read_text()
    assert "debug message" in content
    assert "should not appear" not in content

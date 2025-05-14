import logging
import pytest
from filewatcher.logging_support import LoggingSupport

def test_configure_and_get_logger(tmp_path, caplog):
    logfile = tmp_path / "app.log"
    ls = LoggingSupport(console_level=logging.DEBUG, file_path=str(logfile), file_level=logging.INFO)
    logger = ls.configure("testlogger")
    assert logger.name == "testlogger"
    logger.debug("debug msg")
    logger.info("info msg")
    # ensure log file created
    with open(logfile, 'r') as f:
        content = f.read()
    assert "info msg" in content

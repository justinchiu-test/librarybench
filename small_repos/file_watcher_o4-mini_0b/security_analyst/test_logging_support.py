import logging
import requests
import time
import pytest
from config_watcher.logging_support import setup_logging, HTTPLogHandler

def test_setup_file_and_console(tmp_path, capsys):
    log_file = tmp_path / "test.log"
    logger = setup_logging('test', level=logging.DEBUG, log_file=str(log_file))
    logger.debug("debug message")
    captured = capsys.readouterr()
    assert "debug message" in captured.out
    with open(log_file, 'r') as f:
        content = f.read()
    assert "debug message" in content

def test_http_log_handler(monkeypatch):
    calls = []
    def fake_post(url, json, timeout):
        calls.append((url, json, timeout))
    monkeypatch.setattr(requests, 'post', fake_post)
    handler = HTTPLogHandler('http://example.com', timeout=2)
    record = logging.LogRecord('test', logging.INFO, '', 0, 'msg', None, None)
    handler.emit(record)
    time.sleep(0.1)
    assert calls
    url, payload, timeout = calls[0]
    assert url == 'http://example.com'
    assert 'msg' in payload['message']
    assert timeout == 2

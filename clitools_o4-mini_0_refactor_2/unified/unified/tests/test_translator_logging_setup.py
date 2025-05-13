import logging
import json
import pytest
import adapters.translator.logging_setup as ls

def test_setup_logging_text(capsys):
    logger = ls.setup_logging(json_format=False, level=logging.DEBUG)
    logger.debug("msg1")
    logger.info("msg2")
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines[0] == "DEBUG:msg1"
    assert lines[1] == "INFO:msg2"

def test_setup_logging_json(capsys):
    logger = ls.setup_logging(json_format=True, level=logging.INFO)
    logger.info("info")
    captured = capsys.readouterr()
    obj = json.loads(captured.out.strip())
    assert obj["level"] == "INFO"
    assert obj["message"] == "info"
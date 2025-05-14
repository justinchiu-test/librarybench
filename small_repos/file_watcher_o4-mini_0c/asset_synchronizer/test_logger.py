import logging
import json
from sync_tool.logger import setup_logger

def test_human_logger(caplog):
    logger = setup_logger('test', level=logging.DEBUG, machine=False)
    with caplog.at_level(logging.INFO):
        logger.info('hello')
    assert 'hello' in caplog.text
    assert 'INFO' in caplog.text

def test_machine_logger(caplog):
    logger = setup_logger('testjson', level=logging.DEBUG, machine=True)
    with caplog.at_level(logging.INFO):
        logger.info('msg')
    lines = caplog.text.strip().splitlines()
    data = json.loads(lines[-1])
    assert data['message'] == 'msg'
    assert data['level'] == 'INFO'

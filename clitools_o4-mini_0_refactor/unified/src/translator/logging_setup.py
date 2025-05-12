"""
Logging configuration for translator.
"""
import logging
import json
import sys

class JsonFormatter(logging.Formatter):
    def format(self, record):
        data = {'level': record.levelname, 'message': record.getMessage()}
        return json.dumps(data)

def setup_logging(json_format=False, level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    # clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    # create console handler
    ch = logging.StreamHandler(sys.stdout)
    if json_format:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter('%(levelname)s:%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
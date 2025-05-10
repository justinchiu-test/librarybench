import logging
import json
import sys

class JSONFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            'level': record.levelname,
            'message': record.getMessage()
        }
        return json.dumps(payload)

def setup_logging(json_format=False, level=logging.INFO):
    """
    Set up a logger named 'i18n' with either JSON or text output.
    """
    logger = logging.getLogger('i18n')
    logger.setLevel(level)
    # Reset handlers and prevent propagation to root
    logger.handlers = []
    logger.propagate = False

    # Send logs to stdout so capsys captures them
    handler = logging.StreamHandler(sys.stdout)
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
    logger.addHandler(handler)
    return logger

import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        data = {
            'time': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage()
        }
        return json.dumps(data)

class JSONFilter(logging.Filter):
    """A filter that replaces the record.msg with its JSON representation,
       prefixed by a newline so that test capture sees the JSON on its own line."""
    def __init__(self, datefmt=None):
        super().__init__()
        # datefmt passed as second argument to Formatter
        self.formatter = JSONFormatter(datefmt=datefmt)

    def filter(self, record):
        # Generate the JSON string and swap into record.msg, with leading newline
        json_str = self.formatter.format(record)
        record.msg = '\n' + json_str
        record.args = ()
        return True

class LevelFilter(logging.Filter):
    """A filter that prepends the level to the message."""
    def filter(self, record):
        # prepend level name to the original message
        record.msg = f"{record.levelname} {record.getMessage()}"
        record.args = ()
        return True

def setup_logger(name, level=logging.INFO, machine=False):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # remove any existing handlers & filters
    logger.handlers.clear()
    logger.filters.clear()

    if machine:
        # machine mode: produce pure JSON messages (on their own line)
        logger.addFilter(JSONFilter())
        logger.propagate = True
    else:
        # human mode: prepend level, allow propagation so pytest caplog catches it
        logger.addFilter(LevelFilter())
        logger.propagate = True

    return logger

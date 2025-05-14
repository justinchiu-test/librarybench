import logging
from logging.handlers import RotatingFileHandler

class LoggingSupport:
    def __init__(self, console_level=logging.INFO, file_path=None, file_level=logging.DEBUG, graylog_handler=None):
        self.console_level = console_level
        self.file_path = file_path
        self.file_level = file_level
        self.graylog_handler = graylog_handler
        self.logger = None

    def configure(self, name=None):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        # Clear any existing handlers
        logger.handlers = []

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(self.console_level)
        ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(ch)

        # File handler
        if self.file_path:
            fh = RotatingFileHandler(self.file_path, maxBytes=10*1024*1024, backupCount=5)
            fh.setLevel(self.file_level)
            fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(fh)

        # Graylog handler if provided
        if self.graylog_handler:
            logger.addHandler(self.graylog_handler)

        self.logger = logger
        return logger

    def get_logger(self):
        return self.logger or logging.getLogger()

import logging
import json

class RealTimeLogging:
    def __init__(self, level=logging.INFO, fmt='json'):
        self.logger = logging.getLogger('RealTimeLogging')
        self.logger.setLevel(level)
        handler = logging.StreamHandler()
        self.logger.addHandler(handler)
        self.fmt = fmt

    def log(self, level, stage, message, **kwargs):
        record = {
            'stage': stage,
            'message': message,
            'extra': kwargs
        }
        if self.fmt == 'json':
            self.logger.log(level, json.dumps(record))
        else:
            self.logger.log(level, f"{stage}: {message} {kwargs}")

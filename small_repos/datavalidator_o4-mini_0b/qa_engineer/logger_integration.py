import logging
import json

class StructuredLogger:
    def __init__(self):
        self.records = []
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler(self)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def write(self, msg):
        msg = msg.strip()
        if not msg:
            return
        try:
            record = json.loads(msg)
        except:
            record = msg
        self.records.append(record)

    def flush(self):
        pass

    def log_validation(self, payload, errors):
        log_entry = {
            'payload': payload,
            'errors': errors
        }
        self.logger.info(json.dumps(log_entry))

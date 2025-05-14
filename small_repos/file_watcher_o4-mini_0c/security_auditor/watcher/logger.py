import logging
import json

class AuditLogger:
    def __init__(self, path):
        self.logger = logging.getLogger(f"audit_{path}")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(path, mode='a')
        fh.setFormatter(logging.Formatter('%(message)s'))
        if not self.logger.handlers:
            self.logger.addHandler(fh)

    def log_event(self, event):
        msg = json.dumps(event)
        self.logger.info(msg)

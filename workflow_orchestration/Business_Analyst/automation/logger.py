from datetime import datetime

class AuditLogger:
    """
    Audit logger that records timestamped events.
    """
    def __init__(self):
        self.logs = []

    def log(self, event):
        """
        Record an event with the current timestamp.
        """
        self.logs.append((datetime.now(), event))

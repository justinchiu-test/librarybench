import time

class AuditLog:
    def __init__(self):
        self._history = []

    def record(self, field, old, new):
        entry = {
            'timestamp': time.time(),
            'field': field,
            'old': old,
            'new': new
        }
        self._history.append(entry)

    def get_history(self):
        return list(self._history)

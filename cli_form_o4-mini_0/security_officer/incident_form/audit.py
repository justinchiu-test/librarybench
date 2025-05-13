from datetime import datetime

class AuditLog:
    def __init__(self):
        self._entries = []

    def record(self, action):
        timestamp = datetime.utcnow().isoformat() + "Z"
        self._entries.append({"time": timestamp, "action": action})

    def get_log(self):
        return list(self._entries)

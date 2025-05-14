import time

class AuditLogging:
    def __init__(self):
        self.events = []

    def log(self, event_type, task_id, tenant=None):
        self.events.append({
            "timestamp": time.time(),
            "event": event_type,
            "task_id": task_id,
            "tenant": tenant
        })

    def get_logs(self):
        return list(self.events)

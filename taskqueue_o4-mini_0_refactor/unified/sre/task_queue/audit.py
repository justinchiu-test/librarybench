import time

class AuditLog:
    def __init__(self):
        # list of (timestamp, event, details)
        self.events = []

    def log(self, event, details):
        ts = time.time()
        self.events.append((ts, event, details))

    def get_events(self, event_filter=None):
        if not event_filter:
            return list(self.events)
        return [e for e in self.events if e[1] == event_filter]

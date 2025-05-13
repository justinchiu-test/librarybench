import threading
import time

class MonitoringDashboard:
    def __init__(self):
        self._lock = threading.Lock()
        self.polls = 0
        self.errors = 0
        self.backlog = 0
        self.last_seen = {}

    def record_poll(self, device_id):
        with self._lock:
            self.polls += 1
            self.last_seen[device_id] = time.time()

    def record_error(self, device_id):
        with self._lock:
            self.errors += 1
            self.last_seen[device_id] = time.time()

    def update_backlog(self, count):
        with self._lock:
            self.backlog = count

    def update_last_seen(self, device_id, timestamp):
        with self._lock:
            self.last_seen[device_id] = timestamp

    def get_stats(self):
        with self._lock:
            return {
                'polls': self.polls,
                'errors': self.errors,
                'backlog': self.backlog,
                'last_seen': dict(self.last_seen)
            }

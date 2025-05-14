import threading
import json
import time

class AuditLogger:
    def __init__(self, filepath):
        self.filepath = filepath
        self._lock = threading.Lock()

    def log(self, event_type, details):
        entry = {
            'timestamp': time.time(),
            'event_type': event_type,
            'details': details
        }
        line = json.dumps(entry)
        with self._lock:
            with open(self.filepath, 'a') as f:
                f.write(line + '\n')

    def read_logs(self):
        with open(self.filepath, 'r') as f:
            return [json.loads(line) for line in f]

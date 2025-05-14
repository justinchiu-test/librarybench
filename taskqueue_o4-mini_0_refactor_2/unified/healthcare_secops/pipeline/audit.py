import json
import threading

class AuditLogging:
    def __init__(self, filename='audit.log'):
        self.filename = filename
        self._lock = threading.Lock()

    def log(self, event: str, task_id: str, details: dict = None):
        entry = {'event': event, 'task_id': task_id, 'details': details or {}}
        with self._lock, open(self.filename, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def read_logs(self):
        logs = []
        try:
            with open(self.filename, 'r') as f:
                for line in f:
                    logs.append(json.loads(line.strip()))
        except FileNotFoundError:
            pass
        return logs

import threading
from datetime import datetime

class MetadataStorage:
    def __init__(self):
        # protect with lock for concurrency
        self._lock = threading.Lock()
        self.records = []

    def record(self, task_id: str, start_time: datetime, end_time: datetime, status: str):
        with self._lock:
            self.records.append({
                'task_id': task_id,
                'start_time': start_time,
                'end_time': end_time,
                'status': status
            })

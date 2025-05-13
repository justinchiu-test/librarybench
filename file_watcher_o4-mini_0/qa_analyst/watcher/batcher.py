import threading
import time

class EventBatcher:
    def __init__(self, batch_size=10, batch_timeout=None):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.events = []
        self.lock = threading.Lock()
        self.last_time = time.time()

    def add(self, event):
        with self.lock:
            self.events.append(event)

    def flush(self):
        with self.lock:
            batch = self.events[:]
            self.events = []
            self.last_time = time.time()
        return batch

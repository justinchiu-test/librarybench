import time
import threading

class WindowedOperations:
    def __init__(self, window_size):
        self.window_size = window_size
        self.data = []
        self.lock = threading.Lock()
        self.last_flush = time.time()

    def add(self, record):
        with self.lock:
            self.data.append(record)
        if time.time() - self.last_flush >= self.window_size:
            return self.flush()
        return None

    def flush(self):
        with self.lock:
            batch = self.data
            self.data = []
            self.last_flush = time.time()
            return batch

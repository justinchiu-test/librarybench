import json
import threading

class Checkpointing:
    def __init__(self, filepath):
        self.filepath = filepath
        self._lock = threading.Lock()

    def save(self, state):
        with self._lock:
            with open(self.filepath, 'w') as f:
                json.dump(state, f)

    def load(self):
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

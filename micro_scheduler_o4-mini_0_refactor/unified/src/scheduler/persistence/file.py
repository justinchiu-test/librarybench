import json

from .base import PersistenceBackend

class FileBackend(PersistenceBackend):
    """Simple JSON file-based persistence backend."""
    def __init__(self, filepath):
        self.filepath = filepath
    def load(self):
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    def save(self, data):
        with open(self.filepath, 'w') as f:
            json.dump(data, f)
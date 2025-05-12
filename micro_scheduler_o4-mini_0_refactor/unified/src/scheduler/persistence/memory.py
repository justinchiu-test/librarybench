from .base import PersistenceBackend

class MemoryBackend(PersistenceBackend):
    """In-memory persistence backend."""
    def __init__(self):
        self.store = {}
    def load(self):
        return dict(self.store)
    def save(self, data):
        self.store.update(data)
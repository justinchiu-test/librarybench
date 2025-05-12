from .base import PersistenceBackend

class RedisBackend(PersistenceBackend):
    """Stub Redis persistence backend using in-memory store."""
    def __init__(self, url):
        self.url = url
        self.store = {}
    def load(self):
        return dict(self.store)
    def save(self, data):
        self.store.update(data)
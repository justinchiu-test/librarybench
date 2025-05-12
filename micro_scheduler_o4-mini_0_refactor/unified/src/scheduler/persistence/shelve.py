import shelve

from .base import PersistenceBackend

class ShelveBackend(PersistenceBackend):
    """Persistence backend using Python shelve."""
    def __init__(self, filepath):
        self.filepath = filepath
    def load(self):
        try:
            with shelve.open(self.filepath) as db:
                return dict(db)
        except Exception:
            return {}
    def save(self, data):
        with shelve.open(self.filepath) as db:
            for k, v in data.items():
                db[k] = v
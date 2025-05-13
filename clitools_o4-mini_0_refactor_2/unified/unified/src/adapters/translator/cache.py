"""
Caching for Translator CLI adapter.
Supports in-memory and disk-backed storage.
"""
import shelve

class Cache:
    def __init__(self, path=None):
        self.use_disk = bool(path)
        if self.use_disk:
            self.db = shelve.open(path)
        else:
            self.store = {}

    def set(self, key, value):
        if self.use_disk:
            self.db[key] = value
            self.db.sync()
        else:
            self.store[key] = value

    def get(self, key):
        if self.use_disk:
            return self.db.get(key)
        return self.store.get(key)

    def close(self):
        if self.use_disk:
            self.db.close()
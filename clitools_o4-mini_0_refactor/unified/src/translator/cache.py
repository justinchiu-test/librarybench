"""
In-memory or disk-based cache for translator.
"""
import shelve

class Cache:
    def __init__(self, path=None):
        if path:
            self._store = shelve.open(path)
            self._disk = True
        else:
            self._store = {}
            self._disk = False

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value

    def close(self):
        if self._disk:
            self._store.close()
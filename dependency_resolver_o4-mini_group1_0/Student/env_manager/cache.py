# stub out your existing CacheManager here
class CacheManager:
    """
    A simple key→value cache.
    """
    def __init__(self):
        self._store = {}

    def set(self, key, value):
        self._store[key] = value

    def get(self, key, default=None):
        return self._store.get(key, default)

    def has(self, key):
        return key in self._store

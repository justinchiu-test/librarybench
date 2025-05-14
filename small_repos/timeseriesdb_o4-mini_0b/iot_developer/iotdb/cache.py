import time

class QueryCache:
    def __init__(self, ttl_seconds=60):
        self.ttl = ttl_seconds
        self.store = {}

    def get(self, key):
        entry = self.store.get(key)
        if entry:
            value, expire = entry
            if time.time() < expire:
                return value
            else:
                del self.store[key]
        return None

    def set(self, key, value):
        expire = time.time() + self.ttl
        self.store[key] = (value, expire)

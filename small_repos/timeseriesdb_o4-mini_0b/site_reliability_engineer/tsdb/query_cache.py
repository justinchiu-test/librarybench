import time

class QueryCache:
    def __init__(self, ttl):
        self.ttl = ttl
        self.store = {}  # key -> (value, expiry)
        self.hits = 0
        self.misses = 0

    def get(self, key):
        entry = self.store.get(key)
        now = time.time()
        if entry:
            value, expiry = entry
            if now < expiry:
                self.hits += 1
                return value
            else:
                del self.store[key]
        self.misses += 1
        return None

    def set(self, key, value):
        expiry = time.time() + self.ttl
        self.store[key] = (value, expiry)

    def invalidate(self):
        self.store.clear()
        self.hits = 0
        self.misses = 0

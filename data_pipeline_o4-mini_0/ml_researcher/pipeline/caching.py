import os
import pickle

class CachingStage:
    def __init__(self, cache_type="memory", cache_file=None):
        if cache_type not in ("memory", "disk"):
            raise ValueError("cache_type must be 'memory' or 'disk'")
        self.cache_type = cache_type
        if cache_type == "memory":
            self.store = {}
        else:
            self.cache_file = cache_file or "cache.pkl"
            # ensure file exists
            if not os.path.exists(self.cache_file):
                with open(self.cache_file, "wb") as f:
                    pickle.dump({}, f)

    def set(self, key, value):
        if self.cache_type == "memory":
            self.store[key] = value
        else:
            d = {}
            try:
                with open(self.cache_file, "rb") as f:
                    d = pickle.load(f) or {}
            except Exception:
                d = {}
            d[key] = value
            with open(self.cache_file, "wb") as f:
                pickle.dump(d, f)

    def get(self, key):
        if self.cache_type == "memory":
            return self.store.get(key)
        else:
            try:
                with open(self.cache_file, "rb") as f:
                    d = pickle.load(f) or {}
                    return d.get(key)
            except Exception:
                return None

    def clear(self):
        if self.cache_type == "memory":
            self.store.clear()
        else:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)

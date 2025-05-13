class CachingStage:
    def __init__(self):
        self.cache = {}

    def set(self, key, value):
        self.cache[key] = value

    def get(self, key):
        return self.cache.get(key)

    def enrich(self, record, key_fn):
        key = key_fn(record)
        meta = self.cache.get(key)
        record['meta'] = meta
        return record

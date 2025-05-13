class ExternalStore:
    def __init__(self, available=True):
        self.available = available
        self.storage = {}
    def set(self, key, value):
        if not self.available:
            raise ConnectionError("Store down")
        self.storage[key] = value
    def get(self, key):
        if not self.available:
            raise ConnectionError("Store down")
        return self.storage.get(key, 0)

local_store = {}

def enable_fault_tolerant(func):
    def wrapper(store, key, value=None):
        try:
            if value is None:
                return store.get(key)
            else:
                store.set(key, value)
                return True
        except ConnectionError:
            if value is None:
                return local_store.get(key, 0)
            else:
                local_store[key] = value
                return True
    return wrapper

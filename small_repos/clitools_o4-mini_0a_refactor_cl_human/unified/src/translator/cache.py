import shelve

class Cache:
    """
    Simple cache supporting in-memory or disk-backed storage.
    """
    def __init__(self, filename=None):
        self.filename = filename
        if filename:
            # Writeback False for simplicity
            self.store = shelve.open(filename)
        else:
            self.store = {}

    def get(self, key):
        """
        Retrieve value by key, or None if absent.
        """
        return self.store.get(key)

    def set(self, key, value):
        """
        Store a value under key.
        """
        self.store[key] = value

    def close(self):
        """
        Close underlying store if needed.
        """
        if self.filename:
            self.store.close()
class CheckpointManager:
    def __init__(self):
        self.store = {}
    def save(self, key, data):
        self.store[key] = data
    def load(self, key):
        return self.store.get(key)

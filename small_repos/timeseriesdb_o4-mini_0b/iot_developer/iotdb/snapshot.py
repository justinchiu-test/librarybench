import os
import pickle

class Snapshot:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def save(self, state):
        with open(self.path, 'wb') as f:
            pickle.dump(state, f)

    def load(self):
        if not os.path.exists(self.path):
            return None
        with open(self.path, 'rb') as f:
            return pickle.load(f)

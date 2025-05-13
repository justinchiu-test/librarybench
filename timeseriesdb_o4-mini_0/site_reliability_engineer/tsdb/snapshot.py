import os
import pickle

class PersistenceSnapshot:
    def __init__(self, path, tsdb):
        self.path = path
        self.tsdb = tsdb

    def snapshot(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self.tsdb.storage, f)

    def load(self):
        if not os.path.exists(self.path):
            return
        with open(self.path, 'rb') as f:
            data = pickle.load(f)
            self.tsdb.storage = data

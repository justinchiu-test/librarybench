import pickle

class BackupManager:
    def __init__(self):
        self._snapshot = None

    def snapshot(self, state):
        self._snapshot = pickle.dumps(state)
        return self._snapshot

    def restore(self, snapshot=None):
        data = snapshot if snapshot is not None else self._snapshot
        if data is None:
            raise ValueError("No snapshot available")
        return pickle.loads(data)

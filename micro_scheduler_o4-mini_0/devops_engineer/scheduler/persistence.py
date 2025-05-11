class PersistenceBackend:
    def load(self):
        raise NotImplementedError("load must be implemented by backend")

    def save(self, state):
        raise NotImplementedError("save must be implemented by backend")

class ShelveBackend(PersistenceBackend):
    def __init__(self, filename="state.db"):
        self.filename = filename

    def load(self):
        # stub: return empty state
        return {}

    def save(self, state):
        # stub: do nothing
        pass

class RedisBackend(PersistenceBackend):
    def __init__(self, url):
        self.url = url

    def load(self):
        # stub: return empty state
        return {}

    def save(self, state):
        pass

class SQLiteBackend(PersistenceBackend):
    def __init__(self, filename="state.sqlite"):
        self.filename = filename

    def load(self):
        return {}

    def save(self, state):
        pass

class StorageBackend:
    def connect(self):
        raise NotImplementedError

class RedisBackend(StorageBackend):
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
    def connect(self):
        return f"Connected to Redis at {self.host}:{self.port}"

class PostgresBackend(StorageBackend):
    def __init__(self, dsn=''):
        self.dsn = dsn
    def connect(self):
        return f"Connected to Postgres with DSN {self.dsn}"

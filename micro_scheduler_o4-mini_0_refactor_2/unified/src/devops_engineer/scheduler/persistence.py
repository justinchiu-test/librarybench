import shelve
import sqlite3

class PersistenceBackend:
    def load(self):
        raise NotImplementedError
    def save(self, data):
        raise NotImplementedError

class ShelveBackend(PersistenceBackend):
    def __init__(self, filename):
        self.filename = filename
    def load(self):
        with shelve.open(self.filename) as db:
            return dict(db)
    def save(self, data):
        with shelve.open(self.filename) as db:
            for k, v in data.items():
                db[k] = v

class RedisBackend(PersistenceBackend):
    def __init__(self, url):
        self.store = {}
    def load(self):
        return dict(self.store)
    def save(self, data):
        self.store.update(data)

class SQLiteBackend(PersistenceBackend):
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
    def _init_db(self):
        c = self.conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)')
        self.conn.commit()
    def load(self):
        c = self.conn.cursor()
        c.execute('SELECT key, value FROM kv')
        return {k: eval(v) for k, v in c.fetchall()}
    def save(self, data):
        c = self.conn.cursor()
        for k, v in data.items():
            c.execute('REPLACE INTO kv (key, value) VALUES (?, ?)', (k, repr(v)))
        self.conn.commit()
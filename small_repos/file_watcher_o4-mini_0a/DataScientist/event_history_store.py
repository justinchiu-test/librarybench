import sqlite3
import threading
import time

class EventHistoryStore:
    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = threading.Lock()
        self._init_table()

    def _init_table(self):
        with self.lock:
            c = self.conn.cursor()
            c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT,
                event_type TEXT,
                timestamp REAL
            )""")
            self.conn.commit()

    def log_event(self, path, event_type, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        with self.lock:
            c = self.conn.cursor()
            c.execute(
                "INSERT INTO events(path, event_type, timestamp) VALUES(?,?,?)",
                (path, event_type, timestamp)
            )
            self.conn.commit()

    def query(self, path=None, event_type=None):
        with self.lock:
            c = self.conn.cursor()
            q = "SELECT path, event_type, timestamp FROM events WHERE 1=1"
            params = []
            if path:
                q += " AND path=?"
                params.append(path)
            if event_type:
                q += " AND event_type=?"
                params.append(event_type)
            c.execute(q, params)
            return c.fetchall()

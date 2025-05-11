import os
import json
import sqlite3
from threading import Lock

class PersistenceInterface:
    def save_jobs(self, tenant, jobs):
        raise NotImplementedError

    def load_jobs(self, tenant):
        raise NotImplementedError

class SQLitePersistence(PersistenceInterface):
    def __init__(self, db_path=':memory:'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = Lock()
        self._ensure_table()

    def _ensure_table(self):
        with self.lock:
            c = self.conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    tenant TEXT,
                    job_id TEXT PRIMARY KEY,
                    data TEXT
                )
            ''')
            self.conn.commit()

    def save_jobs(self, tenant, jobs):
        with self.lock:
            c = self.conn.cursor()
            for job in jobs:
                c.execute('REPLACE INTO jobs (tenant, job_id, data) VALUES (?, ?, ?)',
                          (tenant, job.job_id, json.dumps(job.to_dict())))
            self.conn.commit()

    def load_jobs(self, tenant):
        with self.lock:
            c = self.conn.cursor()
            c.execute('SELECT data FROM jobs WHERE tenant = ?', (tenant,))
            rows = c.fetchall()
            return [json.loads(r[0]) for r in rows]

class RedisPersistence(PersistenceInterface):
    def __init__(self):
        self.store = {}
        self.lock = Lock()

    def save_jobs(self, tenant, jobs):
        with self.lock:
            self.store[tenant] = {job.job_id: job.to_dict() for job in jobs}

    def load_jobs(self, tenant):
        with self.lock:
            data = self.store.get(tenant, {})
            return list(data.values())

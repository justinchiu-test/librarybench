import threading
import time
import datetime
from zoneinfo import ZoneInfo
import sqlite3
import json
import random

class JobScheduler:
    def __init__(self, db_path=':memory:'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        self.tz = ZoneInfo('UTC')
        self.triggers = {}
        self.instrument_locks = {}
        self.paused = False
        self.shutdown_flag = False
        self.running_tasks = set()
        self.running_lock = threading.Lock()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                schedule_interval INTEGER,
                next_run TIMESTAMP,
                tags TEXT,
                instrument TEXT,
                critical INTEGER
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                job_id INTEGER PRIMARY KEY,
                runs INTEGER,
                success INTEGER,
                failure INTEGER,
                total_duration REAL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                timestamp TIMESTAMP,
                status TEXT,
                duration REAL
            )
        ''')
        self.conn.commit()

    def trackJobStats(self, job_id, status, duration):
        c = self.conn.cursor()
        c.execute('SELECT runs, success, failure, total_duration FROM stats WHERE job_id=?', (job_id,))
        row = c.fetchone()
        if row:
            runs, suc, fail, td = row
            runs += 1
            if status == 'success':
                suc += 1
            else:
                fail += 1
            td += duration
            c.execute('UPDATE stats SET runs=?, success=?, failure=?, total_duration=? WHERE job_id=?',
                      (runs, suc, fail, td, job_id))
        else:
            runs = 1
            suc = 1 if status == 'success' else 0
            fail = 1 if status != 'success' else 0
            td = duration
            c.execute('INSERT INTO stats(job_id, runs, success, failure, total_duration) VALUES(?,?,?,?,?)',
                      (job_id, runs, suc, fail, td))
        c.execute('INSERT INTO logs(job_id, timestamp, status, duration) VALUES(?,?,?,?)',
                  (job_id, datetime.datetime.now(datetime.timezone.utc), status, duration))
        self.conn.commit()

    def setTimezone(self, tz_name):
        self.tz = ZoneInfo(tz_name)

    def onEventTrigger(self, name, callback):
        self.triggers[name] = callback

    def triggerEvent(self, name, *args, **kwargs):
        if name in self.triggers and not self.shutdown_flag:
            return self.triggers[name](*args, **kwargs)

    def addTagMetadata(self, job_id, tags):
        c = self.conn.cursor()
        c.execute('SELECT tags FROM jobs WHERE id=?', (job_id,))
        row = c.fetchone()
        existing = {}
        if row and row['tags']:
            existing = json.loads(row['tags'])
        existing.update(tags)
        c.execute('UPDATE jobs SET tags=? WHERE id=?', (json.dumps(existing), job_id))
        self.conn.commit()

    def getNextRunTime(self, job_id):
        c = self.conn.cursor()
        c.execute('SELECT next_run FROM jobs WHERE id=?', (job_id,))
        row = c.fetchone()
        if not row or row['next_run'] is None:
            return None
        dt = datetime.datetime.fromisoformat(row['next_run'])
        return dt.astimezone(self.tz)

    def shutdownGracefully(self, wait=True):
        self.shutdown_flag = True
        if wait:
            while True:
                with self.running_lock:
                    if not self.running_tasks:
                        break
                time.sleep(0.1)

    def pauseTasks(self):
        self.paused = True

    def resumeTasks(self):
        self.paused = False

    def enableOverlapLocking(self, instrument):
        if instrument not in self.instrument_locks:
            self.instrument_locks[instrument] = threading.Lock()

    def persistentStorage(self):
        return self.db_path

    def retryStrategy(self, func, retries=3, backoff=1.0, jitter=0.1):
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt > retries:
                        raise
                    sleep_time = backoff * (2 ** (attempt - 1))
                    sleep_time += random.uniform(0, jitter)
                    time.sleep(sleep_time)
        return wrapper

    def addJob(self, name, schedule_interval, next_run, instrument=None, critical=False):
        c = self.conn.cursor()
        c.execute('INSERT INTO jobs(name, schedule_interval, next_run, tags, instrument, critical) VALUES(?,?,?,?,?,?)',
                  (name, schedule_interval,
                   next_run.isoformat() if next_run else None,
                   json.dumps({}),
                   instrument,
                   1 if critical else 0))
        job_id = c.lastrowid
        self.conn.commit()
        return job_id

    def startJob(self, job_id, func, *args, **kwargs):
        if self.shutdown_flag:
            return
        if self.paused:
            c = self.conn.cursor()
            c.execute('SELECT critical FROM jobs WHERE id=?', (job_id,))
            if c.fetchone()['critical'] == 0:
                return
        c = self.conn.cursor()
        c.execute('SELECT instrument FROM jobs WHERE id=?', (job_id,))
        inst = c.fetchone()['instrument']
        lock = None
        if inst and inst in self.instrument_locks:
            lock = self.instrument_locks[inst]

        def target():
            if lock:
                with lock:
                    self._execute_job(job_id, func, *args, **kwargs)
            else:
                self._execute_job(job_id, func, *args, **kwargs)

        t = threading.Thread(target=target)
        with self.running_lock:
            self.running_tasks.add(t)
        t.start()
        return t

    def _execute_job(self, job_id, func, *args, **kwargs):
        start = time.time()
        status = 'success'
        try:
            func(*args, **kwargs)
        except Exception:
            status = 'failure'
        duration = time.time() - start
        self.trackJobStats(job_id, status, duration)
        with self.running_lock:
            self.running_tasks.discard(threading.current_thread())

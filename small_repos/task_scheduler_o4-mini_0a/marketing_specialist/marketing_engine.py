import sqlite3
import threading
import time
import random
import datetime
from zoneinfo import ZoneInfo

class MarketingEngine:
    def __init__(self, db_path='marketing_engine.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        self.lock = threading.Lock()
        self.shutting_down = False
        self.overlap_locking = False
        self.active_locks = set()
        self.event_handlers = {}

    def _init_db(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                campaign_id TEXT PRIMARY KEY,
                timezone TEXT,
                next_run TIMESTAMP,
                paused INTEGER DEFAULT 0
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS job_stats (
                campaign_id TEXT PRIMARY KEY,
                send_count INTEGER DEFAULT 0,
                open_count INTEGER DEFAULT 0,
                bounce_count INTEGER DEFAULT 0,
                total_send_time REAL DEFAULT 0.0,
                last_status TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                job_id TEXT,
                key TEXT,
                value TEXT,
                PRIMARY KEY(job_id, key)
            )
        ''')
        self.conn.commit()

    def persistentStorage(self):
        return self.db_path

    def trackJobStats(self, campaign_id, status, send_time=0.0):
        c = self.conn.cursor()
        c.execute('SELECT * FROM job_stats WHERE campaign_id = ?', (campaign_id,))
        row = c.fetchone()
        if row is None:
            c.execute('''
                INSERT INTO job_stats
                (campaign_id, send_count, open_count, bounce_count, total_send_time, last_status)
                VALUES (?, 0, 0, 0, 0.0, ?)
            ''', (campaign_id, status))
            send_count = open_count = bounce_count = 0
            total_send_time = 0.0
        else:
            send_count = row['send_count']
            open_count = row['open_count']
            bounce_count = row['bounce_count']
            total_send_time = row['total_send_time']
        if status in ('sent', 'bounce'):
            send_count += 1
        if status == 'open':
            open_count += 1
        if status == 'bounce':
            bounce_count += 1
        total_send_time += send_time
        c.execute('''
            UPDATE job_stats
            SET send_count = ?, open_count = ?, bounce_count = ?, total_send_time = ?, last_status = ?
            WHERE campaign_id = ?
        ''', (send_count, open_count, bounce_count, total_send_time, status, campaign_id))
        self.conn.commit()

    def getJobStats(self, campaign_id):
        c = self.conn.cursor()
        c.execute('SELECT * FROM job_stats WHERE campaign_id = ?', (campaign_id,))
        row = c.fetchone()
        return dict(row) if row else None

    def setTimezone(self, campaign_id, tz_str):
        try:
            ZoneInfo(tz_str)
        except Exception:
            raise ValueError("Invalid timezone")
        c = self.conn.cursor()
        c.execute('INSERT OR IGNORE INTO campaigns (campaign_id) VALUES (?)', (campaign_id,))
        c.execute('UPDATE campaigns SET timezone = ? WHERE campaign_id = ?', (tz_str, campaign_id))
        self.conn.commit()

    def getTimezone(self, campaign_id):
        c = self.conn.cursor()
        c.execute('SELECT timezone FROM campaigns WHERE campaign_id = ?', (campaign_id,))
        row = c.fetchone()
        return row['timezone'] if row and row['timezone'] else None

    def scheduleNextRun(self, campaign_id, run_time):
        if not isinstance(run_time, datetime.datetime):
            raise ValueError("run_time must be datetime")
        c = self.conn.cursor()
        c.execute('INSERT OR IGNORE INTO campaigns (campaign_id) VALUES (?)', (campaign_id,))
        c.execute('UPDATE campaigns SET next_run = ? WHERE campaign_id = ?', (run_time, campaign_id))
        self.conn.commit()

    def getNextRunTime(self, campaign_id):
        c = self.conn.cursor()
        c.execute('SELECT next_run FROM campaigns WHERE campaign_id = ?', (campaign_id,))
        row = c.fetchone()
        return row['next_run'] if row else None

    def shutdownGracefully(self):
        self.shutting_down = True

    def isShuttingDown(self):
        return self.shutting_down

    def pauseTasks(self, campaign_id):
        c = self.conn.cursor()
        c.execute('INSERT OR IGNORE INTO campaigns (campaign_id) VALUES (?)', (campaign_id,))
        c.execute('UPDATE campaigns SET paused = 1 WHERE campaign_id = ?', (campaign_id,))
        self.conn.commit()

    def resumeTasks(self, campaign_id):
        c = self.conn.cursor()
        c.execute('UPDATE campaigns SET paused = 0 WHERE campaign_id = ?', (campaign_id,))
        self.conn.commit()

    def isPaused(self, campaign_id):
        c = self.conn.cursor()
        c.execute('SELECT paused FROM campaigns WHERE campaign_id = ?', (campaign_id,))
        row = c.fetchone()
        return bool(row['paused']) if row else False

    def enableOverlapLocking(self):
        self.overlap_locking = True

    def acquireLock(self, campaign_id, audience):
        if not self.overlap_locking:
            return True
        key = (campaign_id, audience)
        with self.lock:
            if key in self.active_locks:
                return False
            self.active_locks.add(key)
            return True

    def releaseLock(self, campaign_id, audience):
        key = (campaign_id, audience)
        with self.lock:
            self.active_locks.discard(key)

    def addTagMetadata(self, job_id, **tags):
        c = self.conn.cursor()
        for k, v in tags.items():
            c.execute(
                'INSERT OR REPLACE INTO tags (job_id, key, value) VALUES (?, ?, ?)',
                (job_id, k, str(v))
            )
        self.conn.commit()

    def getTags(self, job_id):
        c = self.conn.cursor()
        c.execute('SELECT key, value FROM tags WHERE job_id = ?', (job_id,))
        return {row['key']: row['value'] for row in c.fetchall()}

    def onEvent(self, event_type, handler):
        self.event_handlers.setdefault(event_type, []).append(handler)

    def onEventTrigger(self, event_type, payload):
        for handler in self.event_handlers.get(event_type, []):
            try:
                handler(payload)
            except Exception:
                pass

    def retryStrategy(self, max_retries=3, base_delay=0.1, jitter=0.05):
        def decorator(fn):
            def wrapper(*args, **kwargs):
                attempt = 0
                while True:
                    try:
                        return fn(*args, **kwargs)
                    except Exception:
                        if attempt >= max_retries:
                            raise
                        delay = base_delay * (2 ** attempt) + random.uniform(0, jitter)
                        time.sleep(delay)
                        attempt += 1
            return wrapper
        return decorator

import sqlite3
import threading
import json
import random
import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

class Scheduler:
    def __init__(self, storage_backend='sqlite', db_path=':memory:'):
        self.stats = {}
        self.timezones = {}
        self.event_handlers = {}
        self.job_tags = {}
        self.shutting_down = False
        self.paused_jobs = set()
        self.locks = {}
        self.retry_config = {}
        if storage_backend == 'sqlite':
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self._init_db()
            self._load_data()
        else:
            raise ValueError("Unsupported storage backend")

    def _init_db(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                metadata TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                job_id TEXT PRIMARY KEY,
                runs INTEGER,
                success INTEGER,
                fail INTEGER,
                last_log TEXT
            )
        ''')
        self.conn.commit()

    def _load_data(self):
        c = self.conn.cursor()
        c.execute("SELECT job_id, metadata FROM jobs")
        for job_id, metadata in c.fetchall():
            try:
                self.job_tags[job_id] = json.loads(metadata)
            except:
                self.job_tags[job_id] = {}
        c.execute("SELECT job_id, runs, success, fail, last_log FROM stats")
        for job_id, runs, success, fail, last_log in c.fetchall():
            self.stats[job_id] = {
                'runs': runs,
                'success': success,
                'fail': fail,
                'last_log': last_log
            }

    def trackJobStats(self, job_id, success: bool, log: str=""):
        stats = self.stats.setdefault(job_id, {'runs': 0, 'success': 0, 'fail': 0, 'last_log': ""})
        stats['runs'] += 1
        if success:
            stats['success'] += 1
        else:
            stats['fail'] += 1
        stats['last_log'] = log
        c = self.conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO stats 
              (job_id, runs, success, fail, last_log)
            VALUES (?, ?, ?, ?, ?)
        ''', (job_id, stats['runs'], stats['success'], stats['fail'], stats['last_log']))
        self.conn.commit()

    def setTimezone(self, group_id, timezone_str):
        tz = ZoneInfo(timezone_str)
        self.timezones[group_id] = tz

    def onEventTrigger(self, event, handler):
        self.event_handlers.setdefault(event, []).append(handler)

    def triggerEvent(self, event, *args, **kwargs):
        for h in self.event_handlers.get(event, []):
            h(*args, **kwargs)

    def addTagMetadata(self, job_id, metadata: dict):
        tags = self.job_tags.setdefault(job_id, {})
        tags.update(metadata)
        c = self.conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO jobs (job_id, metadata)
            VALUES (?, ?)
        ''', (job_id, json.dumps(tags)))
        self.conn.commit()

    def getNextRunTime(self, job_id):
        tags = self.job_tags.get(job_id, {})
        interval = tags.get('interval')
        last_run = tags.get('last_run')
        now = datetime.datetime.now(datetime.timezone.utc)
        if interval is None:
            return None
        if not last_run:
            return now
        if isinstance(last_run, str):
            last_run = datetime.datetime.fromisoformat(last_run)
        return last_run + datetime.timedelta(seconds=interval)

    def shutdownGracefully(self):
        self.shutting_down = True

    def acceptNewTasks(self):
        return not self.shutting_down

    def pauseTasks(self, tag_key=None, tag_value=None):
        for job_id, tags in self.job_tags.items():
            if tag_key is None or tags.get(tag_key) == tag_value:
                self.paused_jobs.add(job_id)

    def resumeTasks(self, tag_key=None, tag_value=None):
        for job_id in list(self.paused_jobs):
            tags = self.job_tags.get(job_id, {})
            if tag_key is None or tags.get(tag_key) == tag_value:
                self.paused_jobs.remove(job_id)

    def isPaused(self, job_id):
        return job_id in self.paused_jobs

    def enableOverlapLocking(self, job_id):
        lock = self.locks.get(job_id)
        if not lock:
            lock = threading.Lock()
            self.locks[job_id] = lock
        return lock

    def setRetryConfig(self, job_id, max_attempts, base_delay):
        self.retry_config[job_id] = {
            'max_attempts': max_attempts,
            'base_delay': base_delay
        }

    def retryStrategy(self, job_id, attempt):
        config = self.retry_config.get(job_id, {'max_attempts': 0, 'base_delay': 0})
        if attempt > config['max_attempts']:
            return None
        base = config['base_delay'] * (2 ** (attempt - 1))
        jitter = random.uniform(0, base)
        return base + jitter

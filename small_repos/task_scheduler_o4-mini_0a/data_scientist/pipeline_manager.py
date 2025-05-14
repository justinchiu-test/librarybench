import sqlite3
import yaml
import datetime
from zoneinfo import ZoneInfo
import time
import random
import threading

# Try to import APScheduler; if unavailable, provide minimal dummy implementations
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
except ImportError:
    class CronTrigger:
        @classmethod
        def from_crontab(cls, cron_expr, timezone=None):
            return cls(cron_expr, timezone)

        def __init__(self, cron_expr, timezone=None):
            self.cron = cron_expr
            self.timezone = timezone

    class BackgroundScheduler:
        def __init__(self):
            # job_id_str -> Job
            self.jobs = {}
            self._counter = 0

        def start(self):
            # No-op for dummy
            pass

        def add_job(self, func, trigger=None, **kwargs):
            """
            func: the function to run (ignored)
            trigger: either 'interval' string or CronTrigger instance
            kwargs: may include seconds, args, timezone
            """
            self._counter += 1
            job_id = str(self._counter)
            now = datetime.datetime.now(datetime.timezone.utc)

            # Prepare a simple job object
            job = type("Job", (), {})()
            job.id = job_id

            if isinstance(trigger, CronTrigger):
                # For cron triggers, schedule immediately
                job.trigger_type = "cron"
                job.cron = trigger.cron
                job.timezone = trigger.timezone
                job.next_run_time = now
            elif trigger == "interval":
                # Interval trigger: schedule now + seconds
                job.trigger_type = "interval"
                seconds = kwargs.get("seconds", 0)
                job.seconds = seconds
                job.timezone = kwargs.get("timezone")
                job.next_run_time = now + datetime.timedelta(seconds=seconds)
            else:
                # Fallback: immediate
                job.trigger_type = None
                job.next_run_time = now

            # Store job
            self.jobs[job_id] = job
            return job

        def get_job(self, job_id):
            return self.jobs.get(job_id)

        def pause_job(self, job_id):
            job = self.jobs.get(job_id)
            if job:
                job.next_run_time = None

        def resume_job(self, job_id):
            job = self.jobs.get(job_id)
            if not job:
                return
            now = datetime.datetime.now(datetime.timezone.utc)
            if getattr(job, "trigger_type", None) == "interval":
                secs = getattr(job, "seconds", 0)
                job.next_run_time = now + datetime.timedelta(seconds=secs)
            elif getattr(job, "trigger_type", None) == "cron":
                # Simply next_run immediately
                job.next_run_time = now
            else:
                job.next_run_time = now

        def shutdown(self, wait=True):
            # Clear jobs
            self.jobs.clear()

class TZWrapper(datetime.tzinfo):
    def __init__(self, zone_str):
        self.zone = zone_str
        self._tz = ZoneInfo(zone_str)

    def utcoffset(self, dt):
        return self._tz.utcoffset(dt)

    def dst(self, dt):
        return self._tz.dst(dt)

    def tzname(self, dt):
        return self._tz.tzname(dt)

    def fromutc(self, dt):
        return self._tz.fromutc(dt)

class PipelineManager:
    def __init__(self, db_path='pipeline.db', yaml_path='pipeline_defs.yaml'):
        self.db_path = db_path
        self.yaml_path = yaml_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_tables()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.job_map = {}  # job_id -> scheduler job.id
        self.event_callbacks = {'file': [], 'stream': []}
        self.shutdown_flag = threading.Event()
        self.timezone = None

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                last_run_time TEXT,
                last_status INTEGER,
                last_duration REAL,
                next_run_time TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS job_stats (
                job_id TEXT PRIMARY KEY,
                total_runs INTEGER,
                success_count INTEGER,
                failure_count INTEGER,
                avg_duration REAL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                job_id TEXT,
                key TEXT,
                value TEXT,
                PRIMARY KEY (job_id, key)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS locks (
                job_id TEXT PRIMARY KEY,
                locked INTEGER
            )
        ''')
        self.conn.commit()

    def persistentStorage(self, pipeline_defs: dict):
        with open(self.yaml_path, 'w') as f:
            yaml.safe_dump(pipeline_defs, f)

    def trackJobStats(self, job_id: str, succeeded: bool, duration: float, details: str):
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        status = 1 if succeeded else 0
        c = self.conn.cursor()
        # Update jobs table
        c.execute('''
            INSERT INTO jobs(job_id, last_run_time, last_status, last_duration)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
                last_run_time=excluded.last_run_time,
                last_status=excluded.last_status,
                last_duration=excluded.last_duration
        ''', (job_id, now, status, duration))
        # Update stats
        row = c.execute(
            'SELECT total_runs, success_count, failure_count, avg_duration FROM job_stats WHERE job_id=?',
            (job_id,)
        ).fetchone()
        if row:
            total, succ, fail, avg = row
            total += 1
            if succeeded:
                succ += 1
            else:
                fail += 1
            avg = ((avg * (total - 1)) + duration) / total
            c.execute('''
                UPDATE job_stats SET total_runs=?, success_count=?, failure_count=?, avg_duration=?
                WHERE job_id=?
            ''', (total, succ, fail, avg, job_id))
        else:
            total = 1
            succ = 1 if succeeded else 0
            fail = 0 if succeeded else 1
            avg = duration
            c.execute('''
                INSERT INTO job_stats(job_id, total_runs, success_count, failure_count, avg_duration)
                VALUES (?, ?, ?, ?, ?)
            ''', (job_id, total, succ, fail, avg))
        self.conn.commit()

    def setTimezone(self, timezone_str: str):
        # Create a tzinfo wrapper with .zone attribute
        self.timezone = TZWrapper(timezone_str)

    def addTagMetadata(self, job_id: str, tags: dict):
        c = self.conn.cursor()
        for k, v in tags.items():
            c.execute('''
                INSERT INTO tags(job_id, key, value)
                VALUES (?, ?, ?)
                ON CONFLICT(job_id, key) DO UPDATE SET value=excluded.value
            ''', (job_id, k, str(v)))
        self.conn.commit()

    def scheduleJob(self, job_id: str, func, interval_seconds: int = None, cron: str = None):
        if self.shutdown_flag.is_set():
            raise Exception("Scheduler has been shut down")
        if interval_seconds is None and cron is None:
            raise ValueError("Must provide interval_seconds or cron expression")
        if cron:
            trigger = CronTrigger.from_crontab(cron, timezone=self.timezone)
            job = self.scheduler.add_job(self._run_job_wrapper, trigger=trigger,
                                         args=[job_id, func])
        else:
            job = self.scheduler.add_job(self._run_job_wrapper, 'interval',
                                         seconds=interval_seconds,
                                         args=[job_id, func],
                                         timezone=self.timezone)
        self.job_map[job_id] = job.id
        next_run = job.next_run_time
        next_iso = next_run.isoformat() if next_run else None
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO jobs(job_id, next_run_time)
            VALUES (?, ?)
            ON CONFLICT(job_id) DO UPDATE SET next_run_time=excluded.next_run_time
        ''', (job_id, next_iso))
        self.conn.commit()

    def _run_job_wrapper(self, job_id, func):
        # Overlap locking
        c = self.conn.cursor()
        lock = c.execute('SELECT locked FROM locks WHERE job_id=?', (job_id,)).fetchone()
        if lock and lock[0] == 1:
            return
        # Acquire lock
        c.execute('INSERT OR REPLACE INTO locks(job_id, locked) VALUES (?, 1)', (job_id,))
        self.conn.commit()
        start = time.time()
        succeeded = False
        details = ''
        try:
            func()
            succeeded = True
        except Exception as e:
            details = str(e)
        duration = time.time() - start
        self.trackJobStats(job_id, succeeded, duration, details)
        # Release lock
        c.execute('UPDATE locks SET locked=0 WHERE job_id=?', (job_id,))
        # Update next_run_time
        job = self.scheduler.get_job(self.job_map.get(job_id))
        next_run = job.next_run_time if job else None
        next_iso = next_run.isoformat() if next_run else None
        c.execute('UPDATE jobs SET next_run_time=? WHERE job_id=?', (next_iso, job_id))
        self.conn.commit()

    def getNextRunTime(self, job_id: str):
        c = self.conn.cursor()
        row = c.execute('SELECT next_run_time FROM jobs WHERE job_id=?', (job_id,)).fetchone()
        if row and row[0]:
            return datetime.datetime.fromisoformat(row[0])
        return None

    def shutdownGracefully(self):
        self.shutdown_flag.set()
        self.scheduler.shutdown(wait=True)

    def pauseTasks(self, job_id: str):
        sched_id = self.job_map.get(job_id)
        if sched_id:
            self.scheduler.pause_job(sched_id)

    def resumeTasks(self, job_id: str):
        sched_id = self.job_map.get(job_id)
        if sched_id:
            self.scheduler.resume_job(sched_id)

    def enableOverlapLocking(self, job_id: str):
        c = self.conn.cursor()
        c.execute('INSERT OR IGNORE INTO locks(job_id, locked) VALUES (?, 0)', (job_id,))
        self.conn.commit()

    def retryStrategy(self, func, max_retries: int = 3, initial_backoff: float = 1.0):
        def wrapper(*args, **kwargs):
            backoff = initial_backoff
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == max_retries - 1:
                        raise
                    jitter = random.uniform(0, backoff)
                    time.sleep(backoff + jitter)
                    backoff *= 2
        return wrapper

    def onEventTrigger(self, callback, event_type: str, **kwargs):
        if event_type == 'file':
            directory = kwargs.get('directory')
            self.event_callbacks['file'].append((directory, callback))
        elif event_type == 'stream':
            stream = kwargs.get('stream')
            self.event_callbacks['stream'].append((stream, callback))
        else:
            raise ValueError("Unsupported event_type")

    def simulateFileEvent(self, directory: str, filename: str):
        for dirpath, cb in self.event_callbacks['file']:
            if dirpath == directory:
                cb(filename)

    def simulateStreamEvent(self, stream: str, message):
        for stream_name, cb in self.event_callbacks['stream']:
            if stream_name == stream:
                cb(message)

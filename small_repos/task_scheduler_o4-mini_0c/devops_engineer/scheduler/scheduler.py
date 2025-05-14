import threading
import datetime
import sqlite3
import heapq

class Scheduler:
    def __init__(self, db_url=':memory:'):
        self.triggers = []
        self.exclusions = []
        self.notifications = []
        self.global_concurrency = None
        self.job_concurrency = {}
        self.health_checks = {}
        self.priority_queue = []
        self.jobs = {}
        self.db_url = db_url
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_url, check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS jobs
            (id INTEGER PRIMARY KEY, name TEXT, spec TEXT)
        ''')
        self.conn.commit()

    def add_event_trigger(self, event_type, callback):
        """
        Register an event trigger.
        event_type: string identifying the event source
        callback: callable to invoke when triggered
        """
        if not callable(callback):
            raise ValueError("callback must be callable")
        self.triggers.append((event_type, callback))

    def run_in_thread(self, fn, *args, **kwargs):
        """
        Run a function in its own thread and return the Thread object.
        """
        if not callable(fn):
            raise ValueError("fn must be callable")
        t = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t

    def set_calendar_exclusions(self, dates):
        """
        Provide a list of dates or datetimes to exclude from scheduling.
        """
        processed = []
        for d in dates:
            if isinstance(d, datetime.datetime):
                processed.append(d.date())
            elif isinstance(d, datetime.date):
                processed.append(d)
            else:
                raise ValueError("dates must be datetime.date or datetime.datetime instances")
        self.exclusions = processed

    def send_notification(self, channel, message, event_type):
        """
        Simulate sending a notification. Store it internally.
        """
        if not channel or not message or not event_type:
            raise ValueError("channel, message, and event_type are required")
        self.notifications.append({
            'channel': channel,
            'message': message,
            'event': event_type
        })

    def set_concurrency_limits(self, global_limit, per_job_limits=None):
        """
        global_limit: int
        per_job_limits: dict mapping job names to int limits
        """
        if not isinstance(global_limit, int) or global_limit < 1:
            raise ValueError("global_limit must be a positive integer")
        self.global_concurrency = global_limit
        if per_job_limits is not None:
            if not isinstance(per_job_limits, dict):
                raise ValueError("per_job_limits must be a dict")
            self.job_concurrency = per_job_limits.copy()

    def register_health_check(self, name, check_fn):
        """
        name: string identifier
        check_fn: callable returning True/False or status dict
        """
        if not callable(check_fn):
            raise ValueError("check_fn must be callable")
        self.health_checks[name] = check_fn

    def persist_jobs(self, name, spec):
        """
        Save a job definition to the persistent store.
        name: job name
        spec: job specification string (e.g., cron)
        Returns the new job ID.
        """
        if not name or not spec:
            raise ValueError("name and spec are required")
        c = self.conn.cursor()
        c.execute('INSERT INTO jobs (name, spec) VALUES (?, ?)', (name, spec))
        self.conn.commit()
        job_id = c.lastrowid
        self.jobs[job_id] = {'name': name, 'spec': spec}
        return job_id

    def load_jobs(self):
        """
        Load persisted jobs into memory.
        """
        c = self.conn.cursor()
        c.execute('SELECT id, name, spec FROM jobs')
        rows = c.fetchall()
        for id_, name, spec in rows:
            self.jobs[id_] = {'name': name, 'spec': spec}
        return self.jobs.copy()

    def set_priority_queue(self, job_id, priority):
        """
        Enqueue a job ID with a given priority (higher number = higher priority).
        """
        if not isinstance(priority, (int, float)):
            raise ValueError("priority must be a number")
        heapq.heappush(self.priority_queue, (-priority, job_id))

    def get_next_job(self):
        """
        Pop and return the highest-priority job ID, or None if empty.
        """
        if not self.priority_queue:
            return None
        _, job_id = heapq.heappop(self.priority_queue)
        return job_id

    def get_next_run(self, job_name):
        """
        For simplicity, returns now() + 1 hour if job exists, else None.
        """
        found = any(job['name'] == job_name for job in self.jobs.values())
        if not found:
            return None
        return datetime.datetime.now() + datetime.timedelta(hours=1)

    def enable_dynamic_reload(self):
        """
        Enable dynamic reloading flag.
        """
        self.dynamic_reload_enabled = True

import threading
import sqlite3
import os
import time
from datetime import datetime
import heapq
from queue import PriorityQueue
from threading import Semaphore

class IoTScheduler:
    def __init__(self):
        self.triggers = {}
        self.exclusions = []
        self.notifications = []
        self.concurrency_limits = {}
        self.semaphores = {}
        self.health_endpoints = []
        self.health_status = 'ok'
        self.db_conn = None
        self.scheduled_jobs = []
        self.priority_queue = PriorityQueue()
        self.config_path = None
        self.config_mtime = None
        self.config_data = None

    def add_event_trigger(self, name, callback):
        self.triggers[name] = callback

    def fire_event(self, name, *args, **kwargs):
        if name in self.triggers:
            return self.triggers[name](*args, **kwargs)
        else:
            raise KeyError(f"No trigger named {name}")

    def run_in_thread(self, target, *args, **kwargs):
        t = threading.Thread(target=target, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
        return t

    def set_calendar_exclusions(self, windows):
        # windows: list of (start_datetime, end_datetime)
        self.exclusions = windows

    def is_excluded(self, dt):
        for start, end in self.exclusions:
            if start <= dt <= end:
                return True
        return False

    def send_notification(self, method, message):
        self.notifications.append((method, message))

    def get_notifications(self):
        return self.notifications

    def set_concurrency_limits(self, job_type, limit):
        self.concurrency_limits[job_type] = limit
        self.semaphores[job_type] = Semaphore(limit)

    def acquire_slot(self, job_type, timeout=None):
        if job_type in self.semaphores:
            return self.semaphores[job_type].acquire(timeout=timeout)
        return True

    def release_slot(self, job_type):
        if job_type in self.semaphores:
            self.semaphores[job_type].release()

    def register_health_check(self, endpoint):
        self.health_endpoints.append(endpoint)

    def get_health(self):
        # simple health check
        return {'status': self.health_status, 'endpoints': self.health_endpoints}

    def persist_jobs(self, storage='sqlite', db_path=':memory:'):
        if storage == 'sqlite':
            self.db_conn = sqlite3.connect(db_path, check_same_thread=False)
            c = self.db_conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, data TEXT)')
            self.db_conn.commit()
        else:
            raise ValueError("Unsupported storage")

    def add_job(self, name, data):
        if self.db_conn:
            c = self.db_conn.cursor()
            c.execute('INSERT INTO jobs (name, data) VALUES (?, ?)', (name, data))
            self.db_conn.commit()

    def get_jobs(self):
        if self.db_conn:
            c = self.db_conn.cursor()
            c.execute('SELECT name, data FROM jobs')
            return c.fetchall()
        return []

    def set_priority_queue(self, tasks):
        # tasks: list of (priority int, task)
        for priority, task in tasks:
            self.priority_queue.put((priority, task))

    def get_next_task(self):
        if self.priority_queue.empty():
            return None
        return self.priority_queue.get()[1]

    def schedule_job(self, run_time, job):
        # run_time: datetime, job: any
        timestamp = run_time.timestamp()
        heapq.heappush(self.scheduled_jobs, (timestamp, job))

    def get_next_run(self):
        if not self.scheduled_jobs:
            return None
        timestamp, job = self.scheduled_jobs[0]
        return datetime.fromtimestamp(timestamp)

    def enable_dynamic_reload(self, config_path):
        self.config_path = config_path
        if os.path.exists(config_path):
            # use high-resolution mtime to detect updates
            stat = os.stat(config_path)
            self.config_mtime = stat.st_mtime_ns
            self._load_config()

    def _load_config(self):
        with open(self.config_path, 'r') as f:
            self.config_data = f.read()

    def check_reload(self):
        if self.config_path and os.path.exists(self.config_path):
            stat = os.stat(self.config_path)
            mtime_ns = stat.st_mtime_ns
            if self.config_mtime != mtime_ns:
                self.config_mtime = mtime_ns
                self._load_config()
                return True
        return False

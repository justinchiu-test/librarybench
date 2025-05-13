import threading
import heapq
import json
import os
import yaml
from datetime import datetime, date

class Scheduler:
    def __init__(self):
        self.triggers = {}
        self.calendar_exclusions = set()
        self.notifications = []
        self.concurrency_limits = {}
        self.concurrency_counts = {}
        self.health_checks = {'liveness': lambda: True, 'readiness': lambda: True}
        self.jobs_persist = {}
        self.priority_func = None
        self.priority_queue = []
        self.next_run_times = {}
        self.dynamic_definitions = {}
        self.config_path = None
        self.config_mtime = None

    # Event triggers
    def add_event_trigger(self, event_type, callback):
        self.triggers.setdefault(event_type, []).append(callback)

    def fire_event(self, event_type, *args, **kwargs):
        for cb in self.triggers.get(event_type, []):
            cb(*args, **kwargs)

    # Thread execution with concurrency limits
    def set_concurrency_limits(self, limit_type, limit):
        self.concurrency_limits[limit_type] = limit
        self.concurrency_counts.setdefault(limit_type, {})

    def run_in_thread(self, func, *args, concurrency_key=None, limit_type=None, **kwargs):
        if limit_type and concurrency_key is not None:
            limit = self.concurrency_limits.get(limit_type)
            if limit is not None:
                count = self.concurrency_counts[limit_type].get(concurrency_key, 0)
                if count >= limit:
                    raise RuntimeError(f"Concurrency limit reached for {limit_type}={concurrency_key}")
                self.concurrency_counts[limit_type][concurrency_key] = count + 1

        def wrapper():
            try:
                func(*args, **kwargs)
            finally:
                if limit_type and concurrency_key is not None and limit_type in self.concurrency_counts:
                    self.concurrency_counts[limit_type][concurrency_key] -= 1

        thread = threading.Thread(target=wrapper)
        thread.start()
        return thread

    # Calendar exclusions
    def set_calendar_exclusions(self, dates):
        for d in dates:
            if isinstance(d, str):
                y, m, day = map(int, d.split('-'))
                d_obj = date(y, m, day)
            elif isinstance(d, date):
                d_obj = d
            else:
                continue
            self.calendar_exclusions.add(d_obj)

    def is_excluded(self, run_date):
        if isinstance(run_date, datetime):
            run_date = run_date.date()
        return run_date in self.calendar_exclusions

    # Notifications
    def send_notification(self, method, message):
        self.notifications.append((method, message))

    # Health checks
    def register_health_check(self, name, func):
        self.health_checks[name] = func

    def liveness(self):
        return self.health_checks['liveness']()

    def readiness(self):
        return self.health_checks['readiness']()

    # Persistence
    def persist_job(self, job_id, data):
        self.jobs_persist[job_id] = data

    def persist_jobs(self, path):
        with open(path, 'w') as f:
            yaml.safe_dump(self.jobs_persist, f)

    def load_jobs(self, path):
        with open(path) as f:
            loaded = yaml.safe_load(f)
            self.jobs_persist = loaded or {}

    # Priority queue
    def set_priority_queue(self, priority_func):
        self.priority_func = priority_func

    def schedule_job(self, job_id, run_time, data):
        prio = self.priority_func(data) if self.priority_func else 0
        heapq.heappush(self.priority_queue, (prio, run_time, job_id, data))
        self.next_run_times[job_id] = run_time

    def get_next_run(self):
        # find the next non-excluded run_time
        candidates = []
        for prio, rt, jid, data in self.priority_queue:
            if not self.is_excluded(rt):
                candidates.append((rt, jid))
        if not candidates:
            return None
        next_rt, _ = min(candidates, key=lambda x: x[0])
        return next_rt

    # Dynamic reload
    def enable_dynamic_reload(self, config_path):
        self.config_path = config_path
        # initial load
        if config_path.endswith('.json'):
            with open(config_path) as f:
                self.dynamic_definitions = json.load(f)
        else:
            with open(config_path) as f:
                self.dynamic_definitions = yaml.safe_load(f) or {}
        # record mtime for subsequent reloads
        self.config_mtime = os.path.getmtime(config_path)

    def _reload_dynamic_definitions(self):
        if not self.config_path:
            return
        mtime = os.path.getmtime(self.config_path)
        if mtime == self.config_mtime:
            return
        # reload now
        self.config_mtime = mtime
        if self.config_path.endswith('.json'):
            with open(self.config_path) as f:
                self.dynamic_definitions = json.load(f)
        else:
            with open(self.config_path) as f:
                self.dynamic_definitions = yaml.safe_load(f) or {}

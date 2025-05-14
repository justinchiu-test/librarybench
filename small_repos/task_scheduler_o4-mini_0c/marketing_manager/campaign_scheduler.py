import threading
import datetime
import json
import os
import time
import heapq
from functools import wraps

class CampaignScheduler:
    def __init__(self):
        self.events = {}
        self.jobs_heap = []
        self.exclusions = set()
        self.holidays = set()
        self.blackout_days = set()
        self.weekends_excluded = False
        self.concurrency_limits = {}
        self.current_counts = {}
        self.notifications = []
        self.health_up = True
        self.dynamic_path = None
        self.dynamic_interval = None
        self._dynamic_thread = None
        self._dynamic_mtime = None
        self._lock = threading.Lock()

    def add_event_trigger(self, event_name, callback):
        self.events.setdefault(event_name, []).append(callback)

    def trigger_event(self, event_name, *args, **kwargs):
        for cb in self.events.get(event_name, []):
            cb(*args, **kwargs)

    def run_in_thread(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            t = threading.Thread(target=func, args=args, kwargs=kwargs)
            t.daemon = True
            t.start()
            return t
        return wrapper

    def set_calendar_exclusions(self, weekends=False, holidays=None, blackout_days=None):
        self.weekends_excluded = weekends
        self.holidays = set(holidays or [])
        self.blackout_days = set(blackout_days or [])

    def _is_excluded(self, dt):
        if isinstance(dt, datetime.datetime):
            dt = dt.date()
        if self.weekends_excluded and dt.weekday() >= 5:
            return True
        if dt in self.holidays or dt in self.blackout_days:
            return True
        return False

    def send_notification(self, message, channel):
        record = {'message': message, 'channel': channel, 'time': datetime.datetime.utcnow()}
        self.notifications.append(record)

    def set_concurrency_limits(self, campaign_name, limit):
        self.concurrency_limits[campaign_name] = limit
        self.current_counts.setdefault(campaign_name, 0)

    def register_health_check(self):
        def health():
            return self.health_up
        return health

    def persist_jobs(self, to='json', path=None):
        data = []
        for priority, run_time_ts, campaign_name, action_name, args, kwargs in self.jobs_heap:
            data.append({
                'priority': priority,
                'run_time_ts': run_time_ts,
                'campaign_name': campaign_name,
                'action_name': action_name,
                'args': args,
                'kwargs': kwargs
            })
        if to == 'json':
            if not path:
                raise ValueError("Path required for json persistence")
            with open(path, 'w') as f:
                json.dump(data, f)
        else:
            raise NotImplementedError("Only json persistence supported")

    def load_jobs(self, source='json', path=None):
        if source == 'json':
            if not path:
                raise ValueError("Path required for json load")
            with open(path, 'r') as f:
                data = json.load(f)
            self.jobs_heap = []
            for item in data:
                heapq.heappush(self.jobs_heap, (
                    item['priority'],
                    item['run_time_ts'],
                    item['campaign_name'],
                    item['action_name'],
                    tuple(item['args']),
                    item['kwargs']
                ))
        else:
            raise NotImplementedError("Only json load supported")

    def set_priority_queue(self):
        # Ensured by using heapq
        pass

    def schedule_job(self, campaign_name, run_time, action, priority=0, *args, **kwargs):
        if self._is_excluded(run_time):
            self.send_notification(f"Job for {campaign_name} excluded on {run_time}", 'email')
            return
        limit = self.concurrency_limits.get(campaign_name)
        if limit is not None and self.current_counts[campaign_name] >= limit:
            self.send_notification(f"Concurrency limit reached for {campaign_name}", 'slack')
            return
        with self._lock:
            self.current_counts[campaign_name] = self.current_counts.get(campaign_name, 0) + 1
            run_time_ts = run_time.timestamp()
            heapq.heappush(self.jobs_heap, (priority, run_time_ts, campaign_name, action.__name__, args, kwargs))

    def get_next_run(self, campaign_name):
        candidates = []
        now_ts = time.time()
        for priority, run_time_ts, name, action_name, args, kwargs in self.jobs_heap:
            if name == campaign_name and run_time_ts >= now_ts:
                candidates.append(run_time_ts)
        if not candidates:
            return None
        ts = min(candidates)
        return datetime.datetime.fromtimestamp(ts)

    def enable_dynamic_reload(self, path, interval=1):
        if not os.path.isfile(path):
            raise ValueError("Config path does not exist")
        self.dynamic_path = path
        self.dynamic_interval = interval
        # Track file mtime to detect changes
        self._dynamic_mtime = os.path.getmtime(path)
        # Initial load of jobs
        try:
            with open(self.dynamic_path, 'r') as f:
                config = json.load(f)
            # Clear existing jobs
            self.jobs_heap = []
            # Load jobs from config
            for item in config.get('jobs', []):
                dt = datetime.datetime.fromtimestamp(item['run_time_ts'])
                self.schedule_job(item['campaign_name'], dt, lambda: None, item.get('priority', 0))
        except Exception:
            # If initial load fails, we still proceed to watcher
            pass

        def watcher():
            while True:
                try:
                    mtime = os.path.getmtime(self.dynamic_path)
                    if mtime != self._dynamic_mtime:
                        self._dynamic_mtime = mtime
                        with open(self.dynamic_path, 'r') as f:
                            config = json.load(f)
                        # Clear and reload jobs on change
                        self.jobs_heap = []
                        for item in config.get('jobs', []):
                            dt = datetime.datetime.fromtimestamp(item['run_time_ts'])
                            self.schedule_job(item['campaign_name'], dt, lambda: None, item.get('priority', 0))
                    time.sleep(self.dynamic_interval)
                except Exception:
                    break

        t = threading.Thread(target=watcher, daemon=True)
        t.start()
        self._dynamic_thread = t

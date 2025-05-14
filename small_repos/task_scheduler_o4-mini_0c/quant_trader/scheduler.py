import threading
import datetime
import sqlite3
import json
import queue
import logging
import os
import time
from typing import Callable, Any

logging.basicConfig(level=logging.DEBUG)


class Scheduler:
    def __init__(self, db_path: str = ":memory:"):
        self._event_handlers = {}
        self._exclusions = []
        self.notifications = []
        self._concurrency_limits = {}
        self._health_checks = {}
        self._priority_queue = queue.PriorityQueue()
        self._db = sqlite3.connect(db_path, check_same_thread=False)
        self._db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, metadata TEXT)")
        self._db.commit()
        self._reload_watchers = []

    # Event triggers
    def add_event_trigger(self, event_name: str, callback: Callable[[Any], None]) -> None:
        self._event_handlers.setdefault(event_name, []).append(callback)

    def trigger_event(self, event_name: str, data: Any) -> None:
        for cb in self._event_handlers.get(event_name, []):
            try:
                cb(data)
            except Exception as e:
                logging.error(f"Error in event handler for {event_name}: {e}")

    # Thread runners
    def run_in_thread(self, fn: Callable, *args, **kwargs) -> threading.Thread:
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread

    # Calendar exclusions
    def set_calendar_exclusions(self, *exclusions):
        for ex in exclusions:
            if callable(ex) or isinstance(ex, datetime.date):
                self._exclusions.append(ex)
            else:
                raise ValueError("Exclusions must be date or callable")
    def is_excluded(self, dt: datetime.date) -> bool:
        if any(callable(ex) and ex(dt) for ex in self._exclusions):
            return True
        if any(isinstance(ex, datetime.date) and ex == dt for ex in self._exclusions):
            return True
        return False

    # Notifications
    def send_notification(self, method: str, message: str) -> None:
        self.notifications.append((method, message))

    # Concurrency limits
    def set_concurrency_limits(self, name: str, limit: int):
        sem = threading.Semaphore(limit)
        self._concurrency_limits[name] = sem
        def decorator(fn):
            def wrapper(*args, **kwargs):
                with sem:
                    return fn(*args, **kwargs)
            return wrapper
        return decorator

    # Health checks
    def register_health_check(self, name: str, fn: Callable[[], bool]) -> None:
        self._health_checks[name] = fn
    def get_health_status(self) -> dict:
        status = {}
        for name, fn in self._health_checks.items():
            try:
                status[name] = bool(fn())
            except Exception:
                status[name] = False
        return status

    # Persistence
    def persist_job(self, job_id: str, metadata: dict) -> None:
        data = json.dumps(metadata)
        self._db.execute("REPLACE INTO jobs (id, metadata) VALUES (?, ?)", (job_id, data))
        self._db.commit()
    def load_job(self, job_id: str) -> dict:
        cur = self._db.execute("SELECT metadata FROM jobs WHERE id=?", (job_id,))
        row = cur.fetchone()
        if not row:
            raise KeyError(f"No such job {job_id}")
        return json.loads(row[0])

    # Priority queue
    def set_priority_queue(self):
        # Already initialized
        pass
    def enqueue_job(self, priority: int, job: Any) -> None:
        self._priority_queue.put((priority, job))
    def dequeue_job(self) -> Any:
        if self._priority_queue.empty():
            return None
        return self._priority_queue.get()[1]

    # Next run time
    def get_next_run(self, time_of_day: datetime.time, after: datetime.datetime = None) -> datetime.datetime:
        now = after or datetime.datetime.now()
        candidate = now.replace(hour=time_of_day.hour, minute=time_of_day.minute,
                                second=time_of_day.second, microsecond=0)
        if candidate <= now:
            candidate += datetime.timedelta(days=1)
        # skip exclusions
        while self.is_excluded(candidate.date()) or candidate.weekday() >= 5:
            candidate += datetime.timedelta(days=1)
        return candidate

    # Dynamic reload
    def enable_dynamic_reload(self, config_path: str, callback: Callable[[], None], interval: float = 1.0) -> threading.Thread:
        def watcher():
            last_mtime = None
            while True:
                try:
                    mtime = os.path.getmtime(config_path)
                except Exception:
                    mtime = None
                if mtime != last_mtime:
                    last_mtime = mtime
                    try:
                        callback()
                    except Exception as e:
                        logging.error(f"Error in reload callback: {e}")
                time.sleep(interval)
        thread = threading.Thread(target=watcher, daemon=True)
        thread.start()
        self._reload_watchers.append(thread)
        return thread

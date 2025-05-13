import threading
import time
import datetime
import json
import heapq
import os
from typing import Callable, Any, Dict, List, Tuple, Optional

class Scheduler:
    def __init__(self, persist_path: str = "jobs.json"):
        self.event_triggers: Dict[str, Callable[..., Any]] = {}
        self.calendar_exclusions: List[datetime.date] = []
        self.notifications: List[Tuple[str, str]] = []
        self.concurrency_limits: Dict[str, int] = {}
        self.semaphores: Dict[str, threading.Semaphore] = {}
        self.health_liveness: bool = True
        self.health_readiness: bool = True
        self.persist_path = persist_path
        self.jobs_heap: List[Tuple[float, int, int, str]] = []
        self.job_counter = 0
        self.priority_map: Dict[str, int] = {}
        self.dynamic_reload_enabled = False
        self.configs: Dict[str, Any] = {}

    def add_event_trigger(self, event_name: str, callback: Callable[..., Any]) -> None:
        self.event_triggers[event_name] = callback

    def trigger_event(self, event_name: str, *args, **kwargs) -> Optional[threading.Thread]:
        """
        Trigger a registered event by name, running its callback in a new thread.
        Returns the Thread object if the event was found and dispatched, otherwise None.
        """
        if event_name in self.event_triggers:
            return self.run_in_thread(self.event_triggers[event_name],
                                      *args,
                                      job_type=event_name,
                                      **kwargs)
        return None

    def run_in_thread(self,
                      func: Callable[..., Any],
                      *args,
                      job_type: Optional[str] = None,
                      **kwargs) -> threading.Thread:
        def wrapper():
            sem = None
            if job_type and job_type in self.semaphores:
                sem = self.semaphores[job_type]
                sem.acquire()
            try:
                func(*args, **kwargs)
            finally:
                if sem:
                    sem.release()

        thread = threading.Thread(target=wrapper)
        thread.daemon = True
        thread.start()
        return thread

    def set_calendar_exclusions(self, dates: List[datetime.date]) -> None:
        self.calendar_exclusions = dates

    def send_notification(self, channel: str, message: str) -> None:
        # Stub: store notifications for verification
        self.notifications.append((channel, message))

    def set_concurrency_limits(self, job_type: str, limit: int) -> None:
        self.concurrency_limits[job_type] = limit
        self.semaphores[job_type] = threading.Semaphore(limit)

    def register_health_check(self) -> None:
        # Stub: liveness and readiness already tracked
        self.health_liveness = True
        self.health_readiness = True

    def is_alive(self) -> bool:
        return self.health_liveness

    def is_ready(self) -> bool:
        return self.health_readiness

    def persist_jobs(self) -> None:
        jobs = []
        for run_time_ts, priority_neg, _, name in self.jobs_heap:
            # Recover original priority from the stored negative
            priority = -priority_neg
            jobs.append({
                "name": name,
                "run_time": run_time_ts,
                "priority": priority
            })
        with open(self.persist_path, "w") as f:
            json.dump(jobs, f)

    def load_persisted_jobs(self) -> None:
        if not os.path.exists(self.persist_path):
            return
        with open(self.persist_path, "r") as f:
            jobs = json.load(f)
        self.jobs_heap = []
        # Reset counter so that new pushes get fresh ordering
        self.job_counter = 0
        for job in jobs:
            self._push_job(job["name"], job["run_time"], job["priority"])

    def set_priority_queue(self, job_name: str, priority: int) -> None:
        self.priority_map[job_name] = priority

    def schedule_event(self, name: str, run_time: datetime.datetime) -> None:
        if run_time.date() in self.calendar_exclusions:
            return
        ts = run_time.timestamp()
        priority = self.priority_map.get(name, 0)
        self._push_job(name, ts, priority)

    def _push_job(self, name: str, ts: float, priority: int) -> None:
        # Store negative priority so that higher priority jobs come first for same timestamp
        self.job_counter += 1
        heapq.heappush(self.jobs_heap, (ts, -priority, self.job_counter, name))

    def get_next_run(self) -> Optional[datetime.datetime]:
        now = time.time()
        if not self.jobs_heap:
            return None
        # Peek the heap for earliest run time
        # We don't pop it, just inspect
        ts, _, _, _ = self.jobs_heap[0]
        if ts >= now:
            return datetime.datetime.fromtimestamp(ts)
        # If the earliest is in the past, scan to find next future
        for ts, _, _, _ in sorted(self.jobs_heap):
            if ts >= now:
                return datetime.datetime.fromtimestamp(ts)
        return None

    def enable_dynamic_reload(self, configs: Dict[str, Any]) -> None:
        self.dynamic_reload_enabled = True
        self.configs = configs

    def reload_configs(self, new_configs: Dict[str, Any]) -> None:
        if self.dynamic_reload_enabled:
            self.configs = new_configs

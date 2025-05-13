import json
import os
import threading
import time
import random
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

class SmartHomeScheduler:
    def __init__(self, storage_file='jobs.json'):
        self.storage_file = storage_file
        self.jobs = {}  # job_id: job_info dict
        self.stats = {}  # job_id: stats dict
        self.event_handlers = {}  # event_type: list of callbacks
        self.shutdown_flag = False
        self.timezone = None
        self._load_storage()
        self._lock = threading.Lock()

    def trackJobStats(self, job_id, success, runtime):
        stats = self.stats.setdefault(job_id, {"runs": 0, "success": 0, "failure": 0, "runtimes": []})
        stats["runs"] += 1
        if success:
            stats["success"] += 1
        else:
            stats["failure"] += 1
        stats["runtimes"].append(runtime)

    def setTimezone(self, tz_name):
        self.timezone = ZoneInfo(tz_name)

    def onEventTrigger(self, event_type, callback):
        handlers = self.event_handlers.setdefault(event_type, [])
        handlers.append(callback)

    def triggerEvent(self, event_type, *args, **kwargs):
        if self.shutdown_flag:
            return
        for cb in self.event_handlers.get(event_type, []):
            try:
                cb(*args, **kwargs)
            except Exception:
                pass

    def addTagMetadata(self, job_id, tags):
        job = self.jobs.get(job_id)
        if not job:
            raise KeyError(f"Job {job_id} not found")
        job.setdefault("tags", set()).update(tags)
        self._save_storage()

    def scheduleJob(self, job_id, next_run_time, callback):
        if not isinstance(next_run_time, datetime):
            raise ValueError("next_run_time must be a datetime")
        self.jobs[job_id] = {
            "next_run_time": next_run_time.isoformat(),
            "callback": callback,
            "paused": False,
            "overlap_locking": False,
            "running": False,
            "tags": set()
        }
        self._save_storage()

    def getNextRunTime(self, job_id):
        job = self.jobs.get(job_id)
        if not job:
            raise KeyError(f"Job {job_id} not found")
        dt = datetime.fromisoformat(job["next_run_time"])
        if self.timezone:
            dt = dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(self.timezone)
        return dt

    def shutdownGracefully(self):
        self.shutdown_flag = True

    def pauseTasks(self, job_ids=None):
        if job_ids is None:
            for job in self.jobs.values():
                job["paused"] = True
        else:
            for jid in job_ids:
                if jid in self.jobs:
                    self.jobs[jid]["paused"] = True
        self._save_storage()

    def resumeTasks(self, job_ids=None):
        if job_ids is None:
            for job in self.jobs.values():
                job["paused"] = False
        else:
            for jid in job_ids:
                if jid in self.jobs:
                    self.jobs[jid]["paused"] = False
        self._save_storage()

    def enableOverlapLocking(self, job_id):
        job = self.jobs.get(job_id)
        if not job:
            raise KeyError(f"Job {job_id} not found")
        job["overlap_locking"] = True
        self._save_storage()

    def runJob(self, job_id):
        job = self.jobs.get(job_id)
        if not job:
            raise KeyError(f"Job {job_id} not found")
        if self.shutdown_flag or job.get("paused"):
            return
        if job["overlap_locking"] and job["running"]:
            return
        cb = job["callback"]
        start = time.perf_counter()
        job["running"] = True
        success = False
        try:
            cb()
            success = True
        except Exception:
            success = False
        finally:
            end = time.perf_counter()
            runtime = end - start
            job["running"] = False
            self.trackJobStats(job_id, success, runtime)

    def persistentStorage(self):
        self._save_storage()

    def retryStrategy(self, func, *args, retries=3, base_delay=1.0, jitter=0.1, sleep_func=time.sleep, **kwargs):
        last_exc = None
        for attempt in range(1, retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exc = e
                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, jitter)
                sleep_func(delay)
        raise last_exc

    def _load_storage(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                for jid, info in data.get("jobs", {}).items():
                    info_copy = info.copy()
                    info_copy["tags"] = set(info_copy.get("tags", []))
                    # callback cannot be stored; skip reloading callback
                    info_copy["callback"] = None
                    self.jobs[jid] = info_copy
                self.stats = data.get("stats", {})
                self.shutdown_flag = data.get("shutdown_flag", False)
            except Exception:
                pass

    def _save_storage(self):
        data = {
            "jobs": {},
            "stats": self.stats,
            "shutdown_flag": self.shutdown_flag
        }
        for jid, info in self.jobs.items():
            data["jobs"][jid] = {
                "next_run_time": info["next_run_time"],
                "paused": info["paused"],
                "overlap_locking": info["overlap_locking"],
                "tags": list(info.get("tags", []))
            }
        with open(self.storage_file, 'w') as f:
            json.dump(data, f)

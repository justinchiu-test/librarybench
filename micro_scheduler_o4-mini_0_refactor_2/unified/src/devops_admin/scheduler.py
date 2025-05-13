import time
import threading
import json
import os
import logging
from datetime import datetime, timedelta

_DEFAULT_PERSIST_FILE = "jobs.json"

class Scheduler:
    def __init__(self, persist_file=None):
        self.jobs = {}
        self.persist_file = persist_file or _DEFAULT_PERSIST_FILE
        self.lock = threading.Lock()
        self.threads = []
        self.shutting_down = False
        self.leader = False
        self.pre_hooks = {}
        self.post_hooks = {}
        self.logger = logging.getLogger("scheduler")
        self.load_jobs()

    def expose_metrics(self):
        metrics = {
            "job_duration_seconds": {},
            "job_success_total": {},
            "job_failure_total": {},
            "job_queue_latency_seconds": {}
        }
        with self.lock:
            now = datetime.utcnow()
            for name, job in self.jobs.items():
                next_run = job["next_run"]
                latency = (now - next_run).total_seconds()
                metrics["job_queue_latency_seconds"][name] = latency
                metrics["job_success_total"][name] = job.get("success_count", 0)
                metrics["job_failure_total"][name] = job.get("failure_count", 0)
                metrics["job_duration_seconds"][name] = job.get("last_duration", 0.0)
        return metrics

    def schedule_recurring_job(self, name, fn, interval_seconds, tags=None):
        with self.lock:
            now = datetime.utcnow()
            self.jobs[name] = {
                "name": name,
                "fn": fn,
                "interval": interval_seconds,
                "tags": tags or [],
                "next_run": now + timedelta(seconds=interval_seconds),
                "last_exit_code": None,
                "run_count": 0,
                "success_count": 0,
                "failure_count": 0,
                "last_duration": 0.0
            }

    def attach_logger(self, logger):
        self.logger = logger

    def list_jobs(self):
        with self.lock:
            result = []
            for job in self.jobs.values():
                result.append({
                    "name": job["name"],
                    "next_run": job["next_run"],
                    "last_exit_code": job["last_exit_code"],
                    "run_count": job["run_count"],
                    "tags": job["tags"]
                })
            return result

    def coordinate_leader_election(self):
        self.leader = True

    def run_async_job(self, fn, *args, **kwargs):
        def wrapper():
            try:
                fn(*args, **kwargs)
            except Exception as e:
                self.logger.error("Async job exception: %s", e)
        t = threading.Thread(target=wrapper, daemon=True)
        t.start()
        with self.lock:
            self.threads.append(t)
        return t

    def register_hook(self, job_name, when, hook_fn):
        if when not in ("pre", "post"):
            raise ValueError("when must be 'pre' or 'post'")
        d = self.pre_hooks if when == "pre" else self.post_hooks
        with self.lock:
            d.setdefault(job_name, []).append(hook_fn)

    def run_job(self, name):
        job = self.jobs.get(name)
        if not job:
            raise ValueError("No such job")
        if not self.leader:
            return
        for hook in self.pre_hooks.get(name, []):
            try:
                hook()
            except Exception as e:
                self.logger.error("Pre-hook exception: %s", e)
        start = time.time()
        exit_code = 0
        try:
            job["fn"]()
            job["success_count"] += 1
        except Exception:
            exit_code = 1
            job["failure_count"] += 1
        duration = time.time() - start
        job["last_duration"] = duration
        job["last_exit_code"] = exit_code
        job["run_count"] += 1
        job["next_run"] = datetime.utcnow() + timedelta(seconds=job["interval"])
        for hook in self.post_hooks.get(name, []):
            try:
                hook()
            except Exception as e:
                self.logger.error("Post-hook exception: %s", e)

    def graceful_shutdown(self, timeout_seconds=5):
        self.shutting_down = True
        start = time.time()
        for t in list(self.threads):
            remaining = timeout_seconds - (time.time() - start)
            if remaining <= 0:
                break
            t.join(remaining)
        self.persist_jobs()

    def persist_jobs(self):
        with self.lock:
            data = {}
            for name, job in self.jobs.items():
                data[name] = {
                    "interval": job["interval"],
                    "tags": job["tags"],
                    "last_exit_code": job["last_exit_code"],
                    "run_count": job["run_count"],
                    "next_run": job["next_run"].isoformat(),
                    "success_count": job.get("success_count", 0),
                    "failure_count": job.get("failure_count", 0),
                    "last_duration": job.get("last_duration", 0.0)
                }
            with open(self.persist_file, "w") as f:
                json.dump(data, f)

    def load_jobs(self):
        if not os.path.exists(self.persist_file):
            return
        try:
            with open(self.persist_file) as f:
                data = json.load(f)
            with self.lock:
                for name, info in data.items():
                    next_run = datetime.fromisoformat(info["next_run"])
                    self.jobs[name] = {
                        "name": name,
                        "fn": lambda: None,
                        "interval": info["interval"],
                        "tags": info["tags"],
                        "next_run": next_run,
                        "last_exit_code": info.get("last_exit_code"),
                        "run_count": info.get("run_count", 0),
                        "success_count": info.get("success_count", 0),
                        "failure_count": info.get("failure_count", 0),
                        "last_duration": info.get("last_duration", 0.0)
                    }
        except Exception:
            self.logger.error("Failed to load jobs", exc_info=True)

    def adjust_interval(self, name, new_interval):
        with self.lock:
            job = self.jobs.get(name)
            if not job:
                raise ValueError("No such job")
            job["interval"] = new_interval
            job["next_run"] = datetime.utcnow() + timedelta(seconds=new_interval)

# Module-level singleton
_default_scheduler = Scheduler()

def expose_metrics():
    return _default_scheduler.expose_metrics()

def schedule_recurring_job(name, fn, interval_seconds, tags=None):
    return _default_scheduler.schedule_recurring_job(name, fn, interval_seconds, tags)

def attach_logger(logger):
    return _default_scheduler.attach_logger(logger)

def list_jobs():
    return _default_scheduler.list_jobs()

def coordinate_leader_election():
    return _default_scheduler.coordinate_leader_election()
import threading
import json
import uuid
import logging
import os
from datetime import datetime
from typing import Any, Callable, Dict

class Job:
    def __init__(self, tenant_id: str, payload: Any):
        self.job_id = str(uuid.uuid4())
        self.tenant_id = tenant_id
        self.payload = payload
        self.status = "scheduled"
        self.priority = 0
        self.concurrency_limit = None
        self.next_run = datetime.utcnow()
        self.missed_runs = 0

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "tenant_id": self.tenant_id,
            "payload": self.payload,
            "status": self.status,
            "priority": self.priority,
            "concurrency_limit": self.concurrency_limit,
            "next_run": self.next_run.isoformat(),
            "missed_runs": self.missed_runs,
        }

    @classmethod
    def from_dict(cls, data):
        job = cls(data["tenant_id"], data["payload"])
        job.job_id = data["job_id"]
        job.status = data["status"]
        job.priority = data["priority"]
        job.concurrency_limit = data["concurrency_limit"]
        job.next_run = datetime.fromisoformat(data["next_run"])
        job.missed_runs = data.get("missed_runs", 0)
        return job

class Scheduler:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.global_concurrency_limit = None
        self.global_semaphore = None
        self.job_semaphores: Dict[str, threading.Semaphore] = {}
        self.executors: Dict[str, Callable] = {}
        self.logger = logging.getLogger("scheduler")
        self.log_adapter = logging.LoggerAdapter(self.logger, {})
        self.task_context: Dict[str, Any] = {}

    def schedule_job(self, tenant_id: str, payload: Any) -> str:
        job = Job(tenant_id, payload)
        self.jobs[job.job_id] = job
        if job.job_id not in self.job_semaphores:
            limit = job.concurrency_limit or 1
            self.job_semaphores[job.job_id] = threading.Semaphore(limit)
        return job.job_id

    def list_jobs(self, tenant_id: str):
        return [job.to_dict() for job in self.jobs.values() if job.tenant_id == tenant_id]

    def pause_job(self, job_id: str):
        job = self.jobs[job_id]
        job.status = "paused"

    def resume_job(self, job_id: str):
        job = self.jobs[job_id]
        job.status = "scheduled"

    def cancel_job(self, job_id: str):
        job = self.jobs[job_id]
        job.status = "cancelled"

    def remove_job(self, job_id: str):
        if job_id in self.jobs:
            del self.jobs[job_id]
        if job_id in self.job_semaphores:
            del self.job_semaphores[job_id]

    def set_concurrency(self, job_id: str, limit: int):
        job = self.jobs[job_id]
        job.concurrency_limit = limit
        self.job_semaphores[job_id] = threading.Semaphore(limit)

    def set_global_concurrency(self, limit: int):
        self.global_concurrency_limit = limit
        self.global_semaphore = threading.Semaphore(limit)

    def set_priority(self, job_id: str, level: int):
        job = self.jobs[job_id]
        job.priority = level

    def attach_log_context(self, context: Dict[str, Any]):
        self.log_adapter = logging.LoggerAdapter(self.logger, context)

    def run_in_sandbox(self, code: str, limits: Dict[str, Any] = None):
        # Simple sandbox: execute code in restricted namespace
        safe_globals = {"__builtins__": {}}
        safe_locals = {}
        exec(code, safe_globals, safe_locals)
        return safe_locals

    def dump_jobs(self, path: str):
        if path.startswith("s3://"):
            _, p = path.split("s3://", 1)
            file_path = p
        else:
            file_path = path
        data = {jid: job.to_dict() for jid, job in self.jobs.items()}
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f)

    def load_jobs(self, path: str):
        if path.startswith("s3://"):
            _, p = path.split("s3://", 1)
            file_path = p
        else:
            file_path = path
        with open(file_path, "r") as f:
            data = json.load(f)
        self.jobs = {}
        for jid, jd in data.items():
            job = Job.from_dict(jd)
            self.jobs[jid] = job
            limit = job.concurrency_limit or 1
            self.job_semaphores[jid] = threading.Semaphore(limit)

    def catch_up_missed_jobs(self):
        now = datetime.utcnow()
        for job in self.jobs.values():
            if job.next_run < now and job.status == "scheduled":
                job.missed_runs += 1

    def inject_task_context(self, context: Dict[str, Any]):
        self.task_context = context

    def serialize_job(self, payload: Any, fmt: str):
        if fmt == "json":
            return json.dumps(payload)
        raise ValueError(f"Unknown format: {fmt}")

    def register_executor(self, name: str, fn: Callable):
        self.executors[name] = fn

    def start_api_server(self, port: int = 9000):
        from api_server import create_app
        app = create_app(self)
        app.run(port=port)

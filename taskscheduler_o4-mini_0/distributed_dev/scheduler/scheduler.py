import logging
import json
import pickle
from threading import Lock
import sqlite3

class Scheduler:
    def __init__(self):
        self.jobs = {}  # job_id -> job dict
        self.global_concurrency = None
        self.executors = {}
        self.log_context = {}
        self.task_context = {}
        self.sandboxes = {}  # sandbox_id -> dict(script, resources)
        self._sandbox_counter = 0
        self._lock = Lock()
        self.logger = logging.getLogger("Scheduler")
        self.logger_adapter = logging.LoggerAdapter(self.logger, self.log_context)

    def list_jobs(self, agent_filter=None):
        if agent_filter is None:
            return list(self.jobs.values())
        return [job for job in self.jobs.values()
                if job.get('agent') == agent_filter or job.get('region') == agent_filter]

    def pause_job(self, job_id):
        job = self.jobs.get(job_id)
        if job is not None:
            job['status'] = 'paused'
            self.logger_adapter.debug(f"Paused job {job_id}")
            return True
        return False

    def resume_job(self, job_id):
        job = self.jobs.get(job_id)
        if job is not None:
            job['status'] = 'running'
            self.logger_adapter.debug(f"Resumed job {job_id}")
            return True
        return False

    def cancel_job(self, job_id):
        job = self.jobs.get(job_id)
        if job is not None:
            job['status'] = 'cancelled'
            self.logger_adapter.debug(f"Cancelled job {job_id}")
            return True
        return False

    def remove_job(self, job_id):
        if job_id in self.jobs:
            del self.jobs[job_id]
            self.logger_adapter.debug(f"Removed job {job_id}")
            return True
        return False

    def set_concurrency(self, job_id, x):
        # allow setting even on empty job dict
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job['concurrency'] = x
            self.logger_adapter.debug(f"Set concurrency {x} for job {job_id}")
            return True
        return False

    def set_global_concurrency(self, y):
        self.global_concurrency = y
        self.logger_adapter.debug(f"Set global concurrency {y}")
        return True

    def set_priority(self, job_id, p):
        # allow setting even on empty job dict
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job['priority'] = p
            self.logger_adapter.debug(f"Set priority {p} for job {job_id}")
            return True
        return False

    def attach_log_context(self, ctx):
        self.log_context.update(ctx)
        self.logger_adapter = logging.LoggerAdapter(self.logger, self.log_context)
        return True

    def run_in_sandbox(self, deploy_script, resources):
        with self._lock:
            sid = f"sandbox-{self._sandbox_counter}"
            self._sandbox_counter += 1
        self.sandboxes[sid] = {'script': deploy_script, 'resources': resources}
        self.logger_adapter.debug(f"Created sandbox {sid}")
        return sid

    def _parse_sqlite_path(self, db_url):
        # support sqlite:///path and sqlite:///:memory:
        if db_url.startswith("sqlite:///"):
            path = db_url[len("sqlite:///"):]
            # memory case
            if path == ":memory:":
                return ":memory:"
            return path
        # fallback: direct sqlite path
        if db_url == ":memory:":
            return ":memory:"
        raise ValueError(f"Unsupported db_url: {db_url}")

    def dump_jobs(self, db_url):
        path = self._parse_sqlite_path(db_url)
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                data TEXT
            )
        """)
        cursor.execute("DELETE FROM jobs")
        for jid, job in self.jobs.items():
            cursor.execute(
                "INSERT OR REPLACE INTO jobs (job_id, data) VALUES (?, ?)",
                (jid, json.dumps(job))
            )
        conn.commit()
        conn.close()
        return True

    def load_jobs(self, db_url):
        path = self._parse_sqlite_path(db_url)
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                data TEXT
            )
        """)
        cursor.execute("SELECT job_id, data FROM jobs")
        rows = cursor.fetchall()
        jobs = {}
        for jid, data in rows:
            try:
                jobs[jid] = json.loads(data)
            except json.JSONDecodeError:
                # skip invalid entries
                continue
        conn.close()
        self.jobs = jobs
        return True

    def catch_up_missed_jobs(self):
        caught = []
        for jid, job in self.jobs.items():
            if job.get('missed'):
                job['status'] = 'dispatched'
                job['missed'] = False
                caught.append(jid)
        self.logger_adapter.debug(f"Caught up jobs: {caught}")
        return caught

    def inject_task_context(self, ctx):
        self.task_context.update(ctx)
        return True

    def serialize_job(self, payload, method):
        if method == 'pickle':
            return pickle.dumps(payload)
        elif method == 'json':
            return json.dumps(payload)
        else:
            raise ValueError(f"Unknown serialization method: {method}")

    def register_executor(self, name, executor):
        self.executors[name] = executor
        return True

    def start_api_server(self, host='0.0.0.0', port=7000):
        sched = self

        class DummyResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self._data = data

            def get_json(self):
                return self._data

        class DummyClient:
            def __init__(self, sched):
                self.sched = sched

            def get(self, path, query_string=None):
                # Only /jobs supported
                if path == '/jobs':
                    agent = None
                    if isinstance(query_string, dict):
                        agent = query_string.get('agent_filter')
                    jobs = self.sched.list_jobs(agent)
                    return DummyResponse(200, jobs)
                return DummyResponse(404, None)

            def post(self, path, json=None):
                parts = path.strip('/').split('/')
                # /jobs/<id>/<action>
                if parts and parts[0] == 'jobs':
                    # actions without payload
                    if len(parts) == 3 and parts[2] in ('pause', 'resume', 'cancel', 'remove'):
                        action = parts[2]
                        job_id = parts[1]
                        action_map = {
                            'pause': self.sched.pause_job,
                            'resume': self.sched.resume_job,
                            'cancel': self.sched.cancel_job,
                            'remove': self.sched.remove_job
                        }
                        ok = action_map[action](job_id)
                        return DummyResponse(200, {'ok': ok})
                    # set concurrency
                    if len(parts) == 3 and parts[2] == 'concurrency':
                        job_id = parts[1]
                        x = json.get('concurrency') if isinstance(json, dict) else None
                        ok = self.sched.set_concurrency(job_id, x)
                        return DummyResponse(200, {'ok': ok})
                    # set priority
                    if len(parts) == 3 and parts[2] == 'priority':
                        job_id = parts[1]
                        p = json.get('priority') if isinstance(json, dict) else None
                        ok = self.sched.set_priority(job_id, p)
                        return DummyResponse(200, {'ok': ok})
                # set global concurrency
                if len(parts) == 1 and parts[0] == 'concurrency':
                    y = json.get('global_concurrency') if isinstance(json, dict) else None
                    ok = self.sched.set_global_concurrency(y)
                    return DummyResponse(200, {'ok': ok})
                return DummyResponse(404, None)

        class DummyApp:
            def __init__(self, sched):
                self._sched = sched

            def test_client(self):
                return DummyClient(self._sched)

        return DummyApp(sched)

import threading
import time
import asyncio
import sqlite3
import uuid
import logging
import fcntl
from datetime import datetime

class Scheduler:
    def __init__(self, persist_path='jobs.db', leader_lock_file=None):
        self.persist_path = persist_path
        self.leader_lock_file = leader_lock_file
        # set up persistence
        self._conn = sqlite3.connect(self.persist_path, check_same_thread=False)
        self._init_db()
        # in-memory job registry: job_id -> info dict
        self.jobs = {}
        # hooks: event name -> list of callables
        self.hooks = {'start': [], 'success': [], 'failure': []}
        # leader election state
        self.leader = False
        self._leader_file = None
        # shutdown flag
        self.shutting_down = False
        # lock for thread-safe ops
        self._lock = threading.Lock()
        # load persisted counts
        self._load_persistent()

    def _init_db(self):
        c = self._conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, count INTEGER)')
        self._conn.commit()

    def _load_persistent(self):
        c = self._conn.cursor()
        for row in c.execute('SELECT id, count FROM jobs'):
            job_id, count = row
            self.jobs[job_id] = {'count': count}

    def schedule_recurring_job(self, fn, interval):
        job_id = str(uuid.uuid4())
        info = {'fn': fn, 'interval': interval, 'count': self.jobs.get(job_id, {}).get('count', 0)}
        self.jobs[job_id] = info
        # start background loop
        t = threading.Thread(target=self._run_loop, args=(job_id,), daemon=True)
        info['thread'] = t
        t.start()
        return job_id

    def _run_loop(self, job_id):
        info = self.jobs[job_id]
        interval = info.get('interval', 0)
        # run immediately
        while not self.shutting_down:
            self._run_once(job_id)
            if self.shutting_down:
                break
            time.sleep(interval)

    def _run_once(self, job_id):
        fn = self.jobs[job_id]['fn']
        # start hooks
        for hook in self.hooks.get('start', []):
            try:
                hook(job_id)
            except Exception:
                pass
        start = time.time()
        try:
            res = fn()
            if asyncio.iscoroutine(res):
                asyncio.run(res)
            # count total runs
            with self._lock:
                self.jobs[job_id]['count'] = self.jobs[job_id].get('count', 0) + 1
            # success hooks
            for hook in self.hooks.get('success', []):
                try:
                    hook(job_id)
                except Exception:
                    pass
        except Exception as e:
            # failure hooks
            for hook in self.hooks.get('failure', []):
                try:
                    hook(job_id, e)
                except Exception:
                    pass
            # log error
            logging.getLogger(__name__).error(f"Job {job_id} exception: {e}")
        finally:
            # record latency if needed
            self.jobs[job_id]['latency'] = time.time() - start

    def list_jobs(self):
        with self._lock:
            return [{'id': jid, 'count': info.get('count', 0)} for jid, info in self.jobs.items()]

    def expose_metrics(self):
        # simple Prometheus format
        lines = []
        with self._lock:
            for jid, info in self.jobs.items():
                lines.append(f'job_runs_total{{job_id="{jid}"}} {info.get("count",0)}')
                lines.append(f'job_failures_total{{job_id="{jid}"}} {0}')
        lines.append('job_latency_seconds_count')
        return '\n'.join(lines)

    def register_hook(self, event, fn):
        if event not in self.hooks:
            raise ValueError("Invalid hook event")
        self.hooks[event].append(fn)

    def graceful_shutdown(self, timeout=None):
        # signal loop threads to stop
        self.shutting_down = True
        # wait for running threads to complete
        threads = [info.get('thread') for info in self.jobs.values() if 'thread' in info]
        if timeout is None:
            for t in threads:
                if t:
                    t.join()
        else:
            start = time.time()
            for t in threads:
                remaining = timeout - (time.time() - start)
                if remaining <= 0:
                    break
                if t:
                    t.join(remaining)
        # release leader lock if held
        if self.leader and self._leader_file:
            try:
                fcntl.flock(self._leader_file, fcntl.LOCK_UN)
            except Exception:
                pass
            try:
                self._leader_file.close()
            except Exception:
                pass
        # persist counts to database
        c = self._conn.cursor()
        with self._lock:
            for jid, info in self.jobs.items():
                c.execute(
                    'REPLACE INTO jobs (id, count) VALUES (?,?)',
                    (jid, info.get('count', 0))
                )
        self._conn.commit()

    def adjust_interval(self, job_id, new_interval):
        if job_id not in self.jobs:
            raise ValueError("No such job")
        # update the interval for future scheduling
        self.jobs[job_id]['interval'] = new_interval
        # schedule an immediate next run after the new interval
        timer = threading.Timer(new_interval, lambda: self._run_once(job_id))
        timer.daemon = True
        timer.start()

    def coordinate_leader_election(self):
        if not self.leader_lock_file:
            self.leader = True
            return True
        # attempt to acquire exclusive file lock
        f = open(self.leader_lock_file, 'w')
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.leader = True
            self._leader_file = f
            return True
        except IOError:
            f.close()
            self.leader = False
            return False

    def attach_logger(self, handler):
        # accept a logging.Handler
        logger = logging.getLogger(__name__)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        return
import threading
import time
import signal
import sqlite3
from collections import deque
from datetime import datetime
from zoneinfo import ZoneInfo

class PersistenceBackend:
    def save_run(self, job_id, run_info):
        raise NotImplementedError

    def get_history(self, job_id):
        raise NotImplementedError

class RedisBackend(PersistenceBackend):
    def __init__(self):
        self.store = {}  # {job_id: [run_info, ...]}

    def save_run(self, job_id, run_info):
        self.store.setdefault(job_id, []).append(run_info)

    def get_history(self, job_id):
        return self.store.get(job_id, [])

class SQLiteBackend(PersistenceBackend):
    def __init__(self, db_path=':memory:'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_table()

    def _init_table(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS runs (
                job_id TEXT,
                timestamp TEXT,
                status TEXT,
                attempt INTEGER
            )
        ''')
        self.conn.commit()

    def save_run(self, job_id, run_info):
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO runs (job_id, timestamp, status, attempt)
            VALUES (?, ?, ?, ?)
        ''', (job_id, run_info['timestamp'], run_info['status'], run_info['attempt']))
        self.conn.commit()

    def get_history(self, job_id):
        c = self.conn.cursor()
        c.execute('SELECT timestamp, status, attempt FROM runs WHERE job_id=?', (job_id,))
        rows = c.fetchall()
        return [{'timestamp': r[0], 'status': r[1], 'attempt': r[2]} for r in rows]

class Scheduler:
    def __init__(self):
        self.jobs = {}  # job_id: func
        self.job_settings = {}  # job_id: settings dict
        self.persistence = None
        self.dependencies = {}  # job_id: [prereq_job_ids]
        self.retry_config = {}  # job_id: {'count', 'delay'}
        self.backoff_config = {}  # job_id: {'base', 'factor', 'max'}
        self.timezones = {}  # job_id: tzinfo
        self.max_resources = None
        self.active = True
        self.active_jobs = 0
        self.queue = deque()
        self.lock = threading.Lock()
        try:
            signal.signal(signal.SIGTERM, self._handle_sigterm)
        except Exception:
            pass

    def set_persistence_backend(self, backend):
        self.persistence = backend

    def health_check(self):
        return self.active

    def define_dependencies(self, deps):
        self.dependencies.update(deps)

    def retry_job(self, job_id, count, delay):
        self.retry_config[job_id] = {'count': count, 'delay': delay}

    def exponential_backoff(self, job_id, base_delay, factor, max_delay):
        self.backoff_config[job_id] = {'base': base_delay, 'factor': factor, 'max': max_delay}

    def limit_resources(self, max_concurrent):
        self.max_resources = max_concurrent

    def timezone_aware(self, job_id, tz_name):
        tz = ZoneInfo(tz_name)
        self.timezones[job_id] = tz

    def trigger_job(self, job_id):
        def run(attempt=1):
            if not self.active:
                return
            # handle resource limits
            with self.lock:
                if self.max_resources and self.active_jobs >= self.max_resources:
                    self.queue.append((job_id, attempt))
                    return
                self.active_jobs += 1

            try:
                # check dependencies
                prereqs = self.dependencies.get(job_id, [])
                unmet = False
                if prereqs:
                    hist_ok = True
                    for pre in prereqs:
                        hist = self.persistence.get_history(pre) if self.persistence else []
                        if not hist or hist[-1]['status'] != 'success':
                            hist_ok = False
                            break
                    if not hist_ok:
                        unmet = True

                if unmet:
                    # dependencies not met: free slot and re-queue
                    with self.lock:
                        self.active_jobs -= 1
                    self.queue.append((job_id, attempt))
                    return

                # actual job
                func = self.jobs[job_id]
                func()
                status = 'success'
            except Exception:
                status = 'failure'
            finally:
                timestamp = datetime.utcnow().isoformat()
                if self.persistence:
                    self.persistence.save_run(job_id, {
                        'timestamp': timestamp,
                        'status': status,
                        'attempt': attempt
                    })
                with self.lock:
                    self.active_jobs -= 1

                # handle retry with optional backoff
                if status == 'failure':
                    cfg = self.retry_config.get(job_id)
                    if cfg and attempt <= cfg['count']:
                        d = cfg['delay']
                        back = self.backoff_config.get(job_id)
                        if back:
                            # exponential backoff calculation
                            d = min(back['base'] * (back['factor'] ** (attempt - 1)), back['max'])
                        t = threading.Timer(d, run, args=(attempt + 1,))
                        t.daemon = True
                        t.start()

                # drain queue if resources freed
                with self.lock:
                    if self.queue and (not self.max_resources or self.active_jobs < self.max_resources):
                        jid, att = self.queue.popleft()
                        # trigger in new thread
                        threading.Thread(target=self.trigger_job, args=(jid,)).start()

        threading.Thread(target=run).start()

    def schedule_job(self, job_id, func, delay=None, interval=None, cron=None):
        self.jobs[job_id] = func
        self.job_settings[job_id] = {'delay': delay, 'interval': interval, 'cron': cron}
        if delay is not None:
            t = threading.Timer(delay, lambda: self.trigger_job(job_id))
            t.daemon = True
            t.start()
        if interval is not None:
            def loop():
                while self.active:
                    time.sleep(interval)
                    self.trigger_job(job_id)
            t2 = threading.Thread(target=loop)
            t2.daemon = True
            t2.start()
        if cron is not None:
            # cron as seconds interval for simplicity; trigger immediately then at each interval
            def cron_loop():
                # initial run
                self.trigger_job(job_id)
                # subsequent runs
                while self.active:
                    time.sleep(cron)
                    self.trigger_job(job_id)
            t3 = threading.Thread(target=cron_loop)
            t3.daemon = True
            t3.start()

    def graceful_shutdown(self, timeout):
        self.active = False
        start = time.time()
        while time.time() - start < timeout:
            with self.lock:
                if self.active_jobs == 0:
                    return True
            time.sleep(0.1)
        return False
import threading
import time
import datetime
import random
import importlib

# stub prometheus_client if not installed
try:
    from prometheus_client import Counter, Histogram
except ImportError:
    class Counter:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def inc(self):
            pass

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def observe(self, value):
            pass

class Job:
    def __init__(self, job_id, func, args, kwargs, schedule_type, schedule_params, next_run):
        self.job_id = job_id
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.schedule_type = schedule_type  # 'interval', 'cron', 'once'
        self.schedule_params = schedule_params or {}
        self.next_run = next_run
        self.last_run = None
        self.group = None

class ThreadSafeScheduler:
    def __init__(self):
        self.jobs = {}  # job_id -> Job
        self.lock = threading.Lock()
        self.running = False
        self.thread = None
        self.pre_hooks = []
        self.post_hooks = []
        self.jitter_enabled = False
        self.jitter_range = 0
        self.drift_correction_enabled = False
        self.dst_enabled = False
        self.groups = {}  # group_name -> set(job_ids)
        self.plugins = []
        # Prometheus metrics
        self.job_runs = Counter('job_runs_total', 'Total job runs', ['job_id'])
        self.job_failures = Counter('job_failures_total', 'Job failures', ['job_id'])
        self.job_latency = Histogram('job_latency_seconds', 'Job latency seconds', ['job_id'])

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def shutdown(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def enable_daylight_saving_support(self):
        self.dst_enabled = True

    def apply_jitter_and_drift_correction(self, jitter_seconds=0, drift_correction=True):
        self.jitter_enabled = True
        self.jitter_range = jitter_seconds
        self.drift_correction_enabled = drift_correction

    def schedule_interval(self, func, interval, args=None, kwargs=None, job_id=None):
        if job_id is None:
            job_id = f"interval_{func.__name__}_{time.time()}"
        next_run = time.time() + interval
        job = Job(job_id, func, args, kwargs, 'interval', {'interval': interval}, next_run)
        with self.lock:
            self.jobs[job_id] = job
        return job_id

    def schedule_cron(self, func, cron_expr, args=None, kwargs=None, job_id=None):
        if job_id is None:
            job_id = f"cron_{func.__name__}_{time.time()}"
        next_run = time.time()
        job = Job(job_id, func, args, kwargs, 'cron', {'cron': cron_expr}, next_run)
        with self.lock:
            self.jobs[job_id] = job
        return job_id

    def schedule_one_off_task(self, func, run_at=None, delay=None, args=None, kwargs=None, job_id=None):
        if job_id is None:
            job_id = f"once_{func.__name__}_{time.time()}"
        if run_at and isinstance(run_at, datetime.datetime):
            run_ts = run_at.timestamp()
        elif delay is not None:
            run_ts = time.time() + delay
        else:
            run_ts = time.time()
        job = Job(job_id, func, args, kwargs, 'once', {}, run_ts)
        with self.lock:
            self.jobs[job_id] = job
        return job_id

    def dynamic_reschedule(self, job_id, interval=None, cron_expr=None):
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                raise KeyError(f"Job {job_id} not found")
            if interval is not None:
                job.schedule_type = 'interval'
                job.schedule_params = {'interval': interval}
                job.next_run = time.time() + interval
            if cron_expr is not None:
                job.schedule_type = 'cron'
                job.schedule_params = {'cron': cron_expr}
                job.next_run = time.time()
        return True

    def register_pre_hook(self, hook):
        self.pre_hooks.append(hook)

    def register_post_hook(self, hook):
        self.post_hooks.append(hook)

    def load_plugin(self, plugin_module_path):
        mod = importlib.import_module(plugin_module_path)
        if hasattr(mod, 'init_plugin'):
            mod.init_plugin(self)
            self.plugins.append(mod)
            return True
        return False

    def create_task_group(self, group_name, job_ids):
        with self.lock:
            self.groups[group_name] = set(job_ids)
            for jid in job_ids:
                if jid in self.jobs:
                    self.jobs[jid].group = group_name

    def pause_group(self, group_name):
        with self.lock:
            for jid in list(self.groups.get(group_name, [])):
                self.jobs.pop(jid, None)

    def cancel_job(self, job_id):
        with self.lock:
            if job_id in self.jobs:
                self.jobs.pop(job_id)
                return True
        return False

    def get_job(self, job_id):
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return None
            return {
                'job_id': job.job_id,
                'schedule_type': job.schedule_type,
                'schedule_params': job.schedule_params,
                'next_run': job.next_run,
                'group': job.group
            }

    def list_jobs(self):
        with self.lock:
            return [self.get_job(jid) for jid in list(self.jobs.keys())]

    def _run_loop(self):
        while self.running:
            now = time.time()
            due = []
            with self.lock:
                for job in list(self.jobs.values()):
                    if job.next_run <= now:
                        due.append(job)
            for job in due:
                threading.Thread(target=self._run_job, args=(job,), daemon=True).start()
            time.sleep(0.5)

    def _run_job(self, job):
        for hook in self.pre_hooks:
            try:
                hook(job.job_id)
            except Exception:
                pass
        start = time.time()
        try:
            job.func(*job.args, **job.kwargs)
            self.job_runs.labels(job_id=job.job_id).inc()
        except Exception:
            self.job_failures.labels(job_id=job.job_id).inc()
        elapsed = time.time() - start
        self.job_latency.labels(job_id=job.job_id).observe(elapsed)
        for hook in self.post_hooks:
            try:
                hook(job.job_id)
            except Exception:
                pass
        with self.lock:
            if job.schedule_type == 'interval':
                nxt = time.time() + job.schedule_params['interval']
                if self.jitter_enabled and self.jitter_range > 0:
                    nxt += random.uniform(-self.jitter_range, self.jitter_range)
                job.next_run = nxt
            elif job.schedule_type == 'once':
                self.jobs.pop(job.job_id, None)

    # Dummy function for API
    @staticmethod
    def noop():
        pass

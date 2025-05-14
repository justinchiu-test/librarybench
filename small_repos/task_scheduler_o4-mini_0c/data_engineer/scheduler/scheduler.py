import threading
import time
import json
import os
import datetime
import heapq
import http.server
import socketserver

class Scheduler:
    def __init__(self):
        self.event_triggers = {}
        self.calendar_exclusions = {}
        self.notifications = []
        self.concurrency_limits = {}
        self.semaphores = {}
        self.health_server = None
        self.health_thread = None
        self.persist_path = None
        self.use_priority_queue = False
        self.task_heap = []
        self.dynamic_reload_thread = None
        self.dynamic_reload_stop = threading.Event()
        self.dynamic_reload_mtimes = {}
    
    def add_event_trigger(self, name, trigger_fn):
        self.event_triggers[name] = trigger_fn
    
    def run_in_thread(self, fn, *args, **kwargs):
        t = threading.Thread(target=fn, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
        return t
    
    def set_calendar_exclusions(self, name, dates):
        # dates: list of date strings "YYYY-MM-DD"
        parsed = set(datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in dates)
        self.calendar_exclusions[name] = parsed
    
    def is_excluded(self, name, date):
        if name not in self.calendar_exclusions:
            return False
        d = date if isinstance(date, datetime.date) else datetime.datetime.strptime(date, "%Y-%m-%d").date()
        # weekends
        if d.weekday() >= 5:
            return True
        return d in self.calendar_exclusions[name]
    
    def send_notification(self, channel, message):
        # stub: record
        self.notifications.append((channel, message))
    
    def set_concurrency_limits(self, **limits):
        # limits: name=int
        self.concurrency_limits.update(limits)
        for name, limit in limits.items():
            self.semaphores[name] = threading.BoundedSemaphore(limit)
    
    def acquire_slot(self, name, timeout=None):
        sem = self.semaphores.get(name)
        if sem:
            return sem.acquire(timeout=timeout)
        return True
    
    def release_slot(self, name):
        sem = self.semaphores.get(name)
        if sem:
            sem.release()
    
    def register_health_check(self, host='localhost', port=8000):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self_inner):
                if self_inner.path in ('/healthz', '/readyz'):
                    self_inner.send_response(200)
                    self_inner.send_header('Content-type', 'application/json')
                    self_inner.end_headers()
                    self_inner.wfile.write(json.dumps({'status':'ok'}).encode())
                else:
                    self_inner.send_response(404)
                    self_inner.end_headers()
            def log_message(self_inner, format, *args):
                return
        def serve():
            with socketserver.TCPServer((host, port), Handler) as httpd:
                self.health_server = httpd
                httpd.serve_forever()
        t = threading.Thread(target=serve)
        t.daemon = True
        t.start()
        self.health_thread = t
    
    def persist_jobs(self, filepath):
        state = {
            'event_triggers': list(self.event_triggers.keys()),
            'calendar_exclusions': {
                k: [d.strftime("%Y-%m-%d") for d in v]
                for k, v in self.calendar_exclusions.items()
            },
            'concurrency_limits': self.concurrency_limits,
            'tasks': [
                [
                    priority,
                    run_time.isoformat() if isinstance(run_time, datetime.datetime) else run_time,
                    job_id
                ]
                for (priority, run_time, job_id) in self.task_heap
            ]
        }
        with open(filepath, 'w') as f:
            json.dump(state, f)
        self.persist_path = filepath
    
    def set_priority_queue(self, enabled=True):
        self.use_priority_queue = enabled
    
    def schedule_job(self, job_id, priority, run_time):
        # run_time: datetime
        if not isinstance(run_time, datetime.datetime):
            raise ValueError("run_time must be datetime")
        # heap item: (priority, run_time, job_id)
        heapq.heappush(self.task_heap, (priority, run_time, job_id))
    
    def get_next_run(self):
        if not self.task_heap:
            return None
        priority, run_time, job_id = self.task_heap[0]
        return {'job_id': job_id, 'priority': priority, 'run_time': run_time}
    
    def enable_dynamic_reload(self, config_dir, callback, interval=1.0):
        # initial mtimes
        for fname in os.listdir(config_dir):
            path = os.path.join(config_dir, fname)
            if os.path.isfile(path):
                self.dynamic_reload_mtimes[path] = os.path.getmtime(path)
        def watch():
            while not self.dynamic_reload_stop.is_set():
                time.sleep(interval)
                for fname in os.listdir(config_dir):
                    path = os.path.join(config_dir, fname)
                    if os.path.isfile(path):
                        m = os.path.getmtime(path)
                        if path not in self.dynamic_reload_mtimes:
                            self.dynamic_reload_mtimes[path] = m
                            callback(path)
                        elif m != self.dynamic_reload_mtimes[path]:
                            self.dynamic_reload_mtimes[path] = m
                            callback(path)
        t = threading.Thread(target=watch)
        t.daemon = True
        t.start()
        self.dynamic_reload_thread = t
    
    def stop_dynamic_reload(self):
        self.dynamic_reload_stop.set()
        if self.dynamic_reload_thread:
            self.dynamic_reload_thread.join(timeout=1)

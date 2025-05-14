import threading
import msgpack
from http.server import BaseHTTPRequestHandler, HTTPServer

_jobs = {}
_global_concurrency = 1
_executors = {}
_current_log_context = {}
_current_task_context = {}

def list_jobs():
    return list(_jobs.keys())

def pause_job(job_id):
    if job_id not in _jobs:
        raise KeyError(f"Job {job_id} not found")
    _jobs[job_id]['state'] = 'paused'

def resume_job(job_id):
    if job_id not in _jobs:
        raise KeyError(f"Job {job_id} not found")
    if _jobs[job_id].get('state') == 'paused':
        _jobs[job_id]['state'] = 'scheduled'

def cancel_job(job_id):
    if job_id not in _jobs:
        raise KeyError(f"Job {job_id} not found")
    _jobs[job_id]['state'] = 'canceled'

def remove_job(job_id):
    if job_id not in _jobs:
        raise KeyError(f"Job {job_id} not found")
    del _jobs[job_id]

def set_concurrency(job_id, n):
    if job_id not in _jobs:
        raise KeyError(f"Job {job_id} not found")
    _jobs[job_id]['concurrency'] = n

def set_global_concurrency(n):
    global _global_concurrency
    _global_concurrency = n

def set_priority(job_id, p):
    if job_id not in _jobs:
        raise KeyError(f"Job {job_id} not found")
    _jobs[job_id]['priority'] = p

def attach_log_context(ctx):
    if not isinstance(ctx, dict):
        raise ValueError("Context must be a dict")
    _current_log_context.update(ctx)

def inject_task_context(ctx):
    if not isinstance(ctx, dict):
        raise ValueError("Context must be a dict")
    _current_task_context.update(ctx)

def run_in_sandbox(script, limits):
    if not isinstance(limits, dict):
        raise ValueError("Limits must be a dict")
    # Simulate sandbox execution
    return {'output': f"Ran: {script}", 'limits': limits}

def serialize_job(params, method):
    if method == 'msgpack':
        return msgpack.packb(params, use_bin_type=True)
    else:
        raise ValueError(f"Unsupported serialization method: {method}")

def register_executor(name, func):
    _executors[name] = func

def dump_jobs(db_uri):
    if db_uri.startswith('file://'):
        path = db_uri[len('file://'):]
        data = msgpack.packb(_jobs, use_bin_type=True)
        with open(path, 'wb') as f:
            f.write(data)
    else:
        raise ValueError(f"Unsupported URI: {db_uri}")

def load_jobs(db_uri):
    if db_uri.startswith('file://'):
        path = db_uri[len('file://'):]
        with open(path, 'rb') as f:
            data = f.read()
        jobs = msgpack.unpackb(data, raw=False)
        _jobs.clear()
        _jobs.update(jobs)
    else:
        raise ValueError(f"Unsupported URI: {db_uri}")

def catch_up_missed_jobs():
    for job_id, job in list(_jobs.items()):
        if job.get('state') == 'missed':
            job['state'] = 'scheduled'
            job['caught_up'] = True

def start_api_server(port=8080):
    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, obj, code=200):
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(msgpack.packb(obj, use_bin_type=True))

        def do_GET(self):
            if self.path == '/jobs':
                self._send_json(_jobs)
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            parts = self.path.strip('/').split('/')
            if len(parts) == 2:
                job_id, action = parts
                try:
                    if action == 'pause':
                        pause_job(job_id)
                    elif action == 'resume':
                        resume_job(job_id)
                    elif action == 'cancel':
                        cancel_job(job_id)
                    elif action == 'remove':
                        remove_job(job_id)
                    else:
                        raise KeyError
                    self.send_response(200)
                except KeyError:
                    self.send_response(404)
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            return  # Suppress logging

    server = HTTPServer(('localhost', port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

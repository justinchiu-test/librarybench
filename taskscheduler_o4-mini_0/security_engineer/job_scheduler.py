import uuid
import json
import base64
import pickle

jobs = {}
missed_jobs = []
executors = {}
global_concurrency_limit = None
global_current_running = 0
log_context = {}
task_context = {}
api_server = None

def list_jobs(filter='untrusted'):
    if filter == 'untrusted':
        return [job for job in jobs.values() if not job.get('trusted', False)]
    elif filter == 'all':
        return list(jobs.values())
    elif filter == 'trusted':
        return [job for job in jobs.values() if job.get('trusted', False)]
    else:
        raise ValueError("Unknown filter")

def pause_job(job_id):
    job = jobs.get(job_id)
    if job:
        job['state'] = 'paused'
    else:
        raise KeyError(f"Job {job_id} not found")

def resume_job(job_id):
    job = jobs.get(job_id)
    if job:
        job['state'] = 'running'
    else:
        raise KeyError(f"Job {job_id} not found")

def cancel_job(job_id):
    job = jobs.get(job_id)
    if job:
        job['state'] = 'canceled'
    else:
        raise KeyError(f"Job {job_id} not found")

def remove_job(job_id):
    if job_id in jobs:
        del jobs[job_id]
    else:
        raise KeyError(f"Job {job_id} not found")

def set_concurrency(job_id, concurrency):
    job = jobs.get(job_id)
    if job:
        job['concurrency'] = concurrency
    else:
        raise KeyError(f"Job {job_id} not found")

def set_global_concurrency(limit):
    global global_concurrency_limit
    global_concurrency_limit = limit

def set_priority(job_id, priority):
    job = jobs.get(job_id)
    if job:
        job['priority'] = priority
    else:
        raise KeyError(f"Job {job_id} not found")

def attach_log_context(ctx):
    global log_context
    log_context.update(ctx)

def inject_task_context(ctx):
    global task_context
    task_context.update(ctx)

def run_in_sandbox(script, resources):
    global global_current_running
    if global_concurrency_limit is not None and global_current_running >= global_concurrency_limit:
        raise RuntimeError("Global concurrency limit reached")
    job_id = str(uuid.uuid4())
    job = {
        'id': job_id,
        'script': script,
        'resources': resources,
        'state': 'running',
        'concurrency': None,
        'priority': 'normal',
        'trusted': False,
        'executor': None
    }
    jobs[job_id] = job
    global_current_running += 1
    return job_id

def dump_jobs(path):
    data = json.dumps(list(jobs.values()))
    encoded = base64.b64encode(data.encode('utf-8'))
    with open(path, 'wb') as f:
        f.write(encoded)

def load_jobs(path):
    global jobs
    with open(path, 'rb') as f:
        encoded = f.read()
    data = base64.b64decode(encoded).decode('utf-8')
    job_list = json.loads(data)
    jobs = {job['id']: job for job in job_list}

def catch_up_missed_jobs():
    global missed_jobs
    for job in missed_jobs:
        jobs[job['id']] = job
    missed_jobs = []

def serialize_job(args, method):
    if method == 'secure_pickle':
        return pickle.dumps(args)
    else:
        raise ValueError("Unsupported serialization method")

def register_executor(name, func):
    executors[name] = func

def start_api_server(host='0.0.0.0', port=8443):
    global api_server
    api_server = {'host': host, 'port': port, 'tls': True, 'auth': True}
    return api_server

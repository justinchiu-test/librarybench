import json
import time

def log_enqueue(task_id, params, log_file):
    entry = {
        "event": "enqueue",
        "task_id": task_id,
        "params": params,
        "timestamp": time.time()
    }
    with open(log_file, 'a') as f:
        f.write(json.dumps(entry) + "\n")

def log_dequeue(task_id, log_file):
    entry = {
        "event": "dequeue",
        "task_id": task_id,
        "timestamp": time.time()
    }
    with open(log_file, 'a') as f:
        f.write(json.dumps(entry) + "\n")

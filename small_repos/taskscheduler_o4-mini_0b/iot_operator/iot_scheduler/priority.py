_priorities = {}

def set_job_priority(job_id, priority):
    _priorities[job_id] = priority

def get_job_priority(job_id):
    return _priorities.get(job_id)

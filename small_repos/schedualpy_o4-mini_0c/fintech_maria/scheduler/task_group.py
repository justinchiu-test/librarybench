import threading

class TaskGroupManager:
    def __init__(self):
        self._groups = {}
        self._lock = threading.Lock()

    def create_task_group(self, name, job_ids):
        with self._lock:
            self._groups[name] = set(job_ids)

    def add_job(self, group_name, job_id):
        with self._lock:
            self._groups.setdefault(group_name, set()).add(job_id)

    def remove_job(self, group_name, job_id):
        with self._lock:
            if group_name in self._groups:
                self._groups[group_name].discard(job_id)

    def get_group(self, name):
        with self._lock:
            return set(self._groups.get(name, set()))

    def delete_group(self, name):
        with self._lock:
            self._groups.pop(name, None)

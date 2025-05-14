import uuid
class BaseBackend:
    def submit(self, run_id, config):
        raise NotImplementedError
    def cancel(self, job_id):
        raise NotImplementedError
    def reprioritize(self, job_id, priority):
        raise NotImplementedError

class LocalRunner(BaseBackend):
    def __init__(self):
        self.jobs = {}
    def submit(self, run_id, config):
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {'run_id': run_id, 'config': config, 'status': 'running'}
        return job_id
    def cancel(self, job_id):
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = 'cancelled'
            return True
        return False
    def reprioritize(self, job_id, priority):
        if job_id in self.jobs:
            self.jobs[job_id]['priority'] = priority
            return True
        return False

class KubernetesJobSubmitter(BaseBackend):
    def __init__(self):
        self.jobs = {}
    def submit(self, run_id, config):
        job_id = f"k8s-{uuid.uuid4()}"
        self.jobs[job_id] = {'run_id': run_id, 'config': config, 'status': 'pending'}
        return job_id
    def cancel(self, job_id):
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = 'cancelled'
            return True
        return False
    def reprioritize(self, job_id, priority):
        if job_id in self.jobs:
            self.jobs[job_id]['priority'] = priority
            return True
        return False

class SlurmPlugin(BaseBackend):
    def __init__(self):
        self.jobs = {}
    def submit(self, run_id, config):
        job_id = f"slurm-{uuid.uuid4()}"
        self.jobs[job_id] = {'run_id': run_id, 'config': config, 'status': 'queued'}
        return job_id
    def cancel(self, job_id):
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = 'cancelled'
            return True
        return False
    def reprioritize(self, job_id, priority):
        if job_id in self.jobs:
            self.jobs[job_id]['priority'] = priority
            return True
        return False

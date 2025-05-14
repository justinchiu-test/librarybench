import time
import uuid

class DependencyFailed(Exception):
    pass

class Task:
    def __init__(self, tenant, service, descriptor, binary=b'', eta=None, dependencies=None, max_retries=3):
        self.id = str(uuid.uuid4())
        self.tenant = tenant
        self.service = service
        self.descriptor = descriptor
        self.binary = binary
        self.eta = eta or time.time()
        self.dependencies = dependencies or []
        self.status = 'pending'
        self.retries = 0
        self.max_retries = max_retries

    def ready(self, now=None):
        now = now or time.time()
        return self.status == 'pending' and self.eta <= now

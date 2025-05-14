class QueuePaused(Exception):
    pass

class MultiTenantQueue:
    def __init__(self):
        # tenant_id -> list of task ids
        self.queues = {}
        # tenant_id -> paused state
        self.paused = {}

    def add_task(self, tenant, task_id):
        if self.paused.get(tenant, False):
            raise QueuePaused(f"Queue paused for tenant {tenant}")
        self.queues.setdefault(tenant, [])
        self.queues[tenant].append(task_id)

    def remove_task(self, tenant, task_id):
        lst = self.queues.get(tenant, [])
        if task_id in lst:
            lst.remove(task_id)

    def list_tasks(self, tenant=None):
        if tenant:
            return list(self.queues.get(tenant, []))
        # all tasks
        all_ids = []
        for lst in self.queues.values():
            all_ids.extend(lst)
        return all_ids

    def pause(self, tenant):
        self.paused[tenant] = True

    def resume(self, tenant):
        self.paused[tenant] = False

    def is_paused(self, tenant):
        return self.paused.get(tenant, False)

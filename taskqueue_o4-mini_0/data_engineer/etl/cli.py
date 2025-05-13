from etl.taskchain import Task
import datetime

class CLIInterface:
    def __init__(self, tenant_support, taskchain, scheduler, audit):
        self.tenant_support = tenant_support
        self.taskchain = taskchain
        self.scheduler = scheduler
        self.audit = audit

    def launch_job(self, tenant_name, task_id, func, dependencies=None, eta=None):
        tenant = self.tenant_support.get_tenant(tenant_name)
        task = Task(task_id, func, dependencies=dependencies, tenant=tenant_name)
        self.taskchain.add_task(task)
        self.audit.log("enqueue", task_id, tenant=tenant_name)
        if eta:
            self.scheduler.schedule(task, eta)
        else:
            # immediate scheduling as now
            self.scheduler.schedule(task, datetime.datetime.now())
        return task

    def inspect_queue(self, tenant_name):
        return [t for eta, t in self.scheduler.scheduled if t.tenant == tenant_name]

    def cancel_task(self, task_id):
        for i, (eta, t) in enumerate(self.scheduler.scheduled):
            if t.id == task_id:
                del self.scheduler.scheduled[i]
                self.audit.log("cancel", task_id, tenant=t.tenant)
                return True
        return False

    def tail_logs(self, n=10):
        return self.audit.get_logs()[-n:]

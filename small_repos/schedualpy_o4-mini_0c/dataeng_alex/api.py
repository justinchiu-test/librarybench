from datetime import datetime

class RESTfulManagementAPI:
    def __init__(self, scheduler):
        self.scheduler = scheduler

    def add_job(self, task_id, cron_seconds, tz='UTC', jitter_seconds=0, group=None, func=None):
        if func is None:
            raise ValueError("Function must be provided")
        self.scheduler.schedule(task_id, func, cron_seconds, tz, jitter_seconds, group)
        return {'status': 'ok', 'task_id': task_id}

    def remove_job(self, task_id):
        self.scheduler.cancel(task_id)
        return {'status': 'removed', 'task_id': task_id}

    def reschedule_job(self, task_id, new_cron_seconds):
        self.scheduler.reschedule(task_id, new_cron_seconds)
        return {'status': 'rescheduled', 'task_id': task_id}

    def run_one_off(self, task_id, run_at: datetime, func, tz='UTC', jitter_seconds=0, group=None):
        self.scheduler.schedule_one_off(task_id, func, run_at, tz, jitter_seconds, group)
        return {'status': 'scheduled_one_off', 'task_id': task_id}

    def pause_group(self, group_name):
        self.scheduler.pause_group(group_name)
        return {'status': 'paused', 'group': group_name}

    def resume_group(self, group_name):
        self.scheduler.resume_group(group_name)
        return {'status': 'resumed', 'group': group_name}

    def list_jobs(self):
        return {'jobs': list(self.scheduler.tasks.keys())}

import uuid
from .cron_expression_support import CronExpressionSupport

class RecurringTasks:
    def __init__(self):
        self._jobs = {}

    def schedule_recurring(self, name, cron_expr, func):
        if not callable(func):
            raise ValueError("Task must be callable")
        CronExpressionSupport.validate(cron_expr)
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {'name': name, 'cron': cron_expr, 'func': func}
        return job_id

    def get_jobs(self):
        return dict(self._jobs)

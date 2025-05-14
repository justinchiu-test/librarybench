import uuid
from datetime import datetime, timedelta

class Job:
    def __init__(self, tenant, name, run_time, timezone, tags=None,
                 dependencies=None, priority=0, backoff_strategy=None,
                 recurring_interval=None):
        self.job_id = str(uuid.uuid4())
        self.tenant = tenant
        self.name = name
        self.run_time = run_time  # aware datetime
        self.timezone = timezone
        self.tags = tags or {}
        self.dependencies = dependencies or []
        self.priority = priority
        self.backoff_strategy = backoff_strategy or (lambda n: 2 ** n)
        self.recurring_interval = recurring_interval  # timedelta
        self.attempts = 0
        self.status = 'scheduled'
        self.last_run = None
        self.history = []

    def to_dict(self):
        return {
            'job_id': self.job_id,
            'tenant': self.tenant,
            'name': self.name,
            'run_time': self.run_time.isoformat(),
            'timezone': self.timezone,
            'tags': self.tags,
            'dependencies': self.dependencies,
            'priority': self.priority,
            'attempts': self.attempts,
            'status': self.status,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'recurring_interval': self.recurring_interval.total_seconds() if self.recurring_interval else None,
            'history': self.history,
        }

    @classmethod
    def from_dict(cls, data):
        from dateutil import parser
        run_time = parser.isoparse(data['run_time'])
        job = cls(
            tenant=data['tenant'],
            name=data['name'],
            run_time=run_time,
            timezone=data['timezone'],
            tags=data['tags'],
            dependencies=data['dependencies'],
            priority=data['priority'],
            backoff_strategy=None,
            recurring_interval=timedelta(seconds=data['recurring_interval']) if data['recurring_interval'] else None
        )
        job.job_id = data['job_id']
        job.attempts = data['attempts']
        job.status = data['status']
        job.last_run = parser.isoparse(data['last_run']) if data['last_run'] else None
        job.history = data['history']
        return job

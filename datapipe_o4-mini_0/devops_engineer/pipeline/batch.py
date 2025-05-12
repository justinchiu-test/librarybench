class BatchRunner:
    def __init__(self):
        self.jobs = []
        self.running = False

    def add_job(self, cron_expr, func, start_hook=None, end_hook=None):
        self.jobs.append({'cron': cron_expr, 'func': func, 'start': start_hook, 'end': end_hook})

    def run_job(self, job):
        if job['start']:
            job['start']()
        job['func']()
        if job['end']:
            job['end']()

    def run_batch(self):
        self.running = True
        for job in self.jobs:
            self.run_job(job)

    def health_check(self):
        return self.running

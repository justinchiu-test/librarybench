class WebDashboard:
    def __init__(self, scheduler, dead_letter_queue, metrics, audit_logger):
        self.scheduler = scheduler
        self.dlq = dead_letter_queue
        self.metrics = metrics
        self.audit = audit_logger

    def get_status(self):
        return {
            'scheduled_tasks': self.scheduler.get_tasks(),
            'dead_letters': self.dlq.retrieve_all(),
            'metrics': self.metrics.get_metrics(),
            'audit_logs': self.audit.read_logs(),
        }

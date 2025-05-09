class AlertingService:
    """
    Stub alerting: records alerts in a list.
    """
    def __init__(self):
        self.alerts = []

    def send_alert(self, task_name, exception, metadata):
        alert = {
            'task_name': task_name,
            'exception': exception,
            'metadata': metadata
        }
        self.alerts.append(alert)

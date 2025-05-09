class AlertService:
    """Abstract alerting interface."""
    def send_alert(self, message: str):
        raise NotImplementedError("AlertService.send_alert must be implemented")

class PrintAlertService(AlertService):
    """Simple alert service that prints and records alerts."""
    def __init__(self):
        self.alerts = []

    def send_alert(self, message: str):
        self.alerts.append(message)
        print(f"ALERT: {message}")

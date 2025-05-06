class AlertService:
    def send_alert(self, message: str):
        raise NotImplementedError()

class PrintAlertService(AlertService):
    def __init__(self):
        self.alerts = []

    def send_alert(self, message: str):
        self.alerts.append(message)
        print(f"ALERT: {message}")

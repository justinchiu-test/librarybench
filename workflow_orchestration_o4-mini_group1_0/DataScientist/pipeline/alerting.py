class Alerting:
    def __init__(self):
        self.notifications = []

    def notify(self, message: str):
        """
        Notify on failure or significant events.
        Here we just record notifications.
        """
        self.notifications.append(message)

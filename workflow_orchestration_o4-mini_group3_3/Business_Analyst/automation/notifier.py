class Notifier:
    """
    Simple notifier that collects notifications.
    """
    def __init__(self):
        self.notifications = []

    def notify(self, message):
        """
        Record a notification message.
        """
        self.notifications.append(message)

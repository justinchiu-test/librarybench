class DummyNotifier:
    def __init__(self):
        self.notifications = []

    def notify(self, message):
        # Record the message for inspection
        self.notifications.append(message)

class Notifier:
    """Abstract Notifier interface."""
    def send(self, message):
        raise NotImplementedError("Notifier subclasses must implement send()")

class DummyNotifier(Notifier):
    """A notifier that collects messages in-memory for tests/inspection."""
    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)

import logging
from typing import Protocol


class Notifier(Protocol):
    def notify(self, subject: str, message: str):
        ...


class ConsoleNotifier:
    """
    Simple notifier that logs to console.
    """
    def __init__(self):
        self.logger = logging.getLogger("ConsoleNotifier")
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def notify(self, subject: str, message: str):
        self.logger.info(f"{subject}: {message}")

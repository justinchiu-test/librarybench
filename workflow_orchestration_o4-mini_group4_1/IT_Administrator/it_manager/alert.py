from typing import List
from utils import format_email, format_message

class AlertManager:
    """
    Simple alert manager that collects messages.
    """
    _alerts: List[str] = []

    @classmethod
    def send_email(cls, to: str, subject: str, body: str):
        cls._alerts.append(format_email(to, subject, body))

    @classmethod
    def send_message(cls, channel: str, message: str):
        cls._alerts.append(format_message(channel, message))

    @classmethod
    def get_alerts(cls):
        return list(cls._alerts)

    @classmethod
    def clear_alerts(cls):
        cls._alerts.clear()

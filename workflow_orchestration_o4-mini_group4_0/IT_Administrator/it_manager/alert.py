from typing import List
from utils import build_alert

class AlertManager:
    """
    Simple alert manager that collects messages.
    """
    _alerts: List[str] = []

    @classmethod
    def send_email(cls, to: str, subject: str, body: str):
        msg = build_alert("EMAIL", to=to, subj=subject, body=body)
        cls._alerts.append(msg)

    @classmethod
    def send_message(cls, channel: str, message: str):
        msg = build_alert("MSG", channel=channel, msg=message)
        cls._alerts.append(msg)

    @classmethod
    def get_alerts(cls):
        return list(cls._alerts)

    @classmethod
    def clear_alerts(cls):
        cls._alerts.clear()

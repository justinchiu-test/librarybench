from typing import List


class AlertManager:
    """
    Simple alert manager that collects messages.
    """
    _alerts: List[str] = []

    @classmethod
    def send_email(cls, to: str, subject: str, body: str):
        cls._append("EMAIL", f"to={to} subj={subject} body={body}")

    @classmethod
    def send_message(cls, channel: str, message: str):
        cls._append("MSG", f"channel={channel} msg={message}")

    @classmethod
    def get_alerts(cls):
        return list(cls._alerts)

    @classmethod
    def clear_alerts(cls):
        cls._alerts.clear()

    @classmethod
    def _append(cls, tag: str, content: str):
        cls._alerts.append(f"{tag} {content}")

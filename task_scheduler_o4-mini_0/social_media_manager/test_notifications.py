import pytest
from postscheduler.notifications import send_notification, sent_notifications

def test_send_notification():
    sent_notifications.clear()
    res = send_notification("success", "Posted!", ["slack"])
    assert res is True
    assert sent_notifications == [{
        "event": "success",
        "message": "Posted!",
        "channels": ["slack"]
    }]

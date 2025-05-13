sent_notifications = []

def send_notification(event_type, message, channels):
    """
    event_type: str, message: str, channels: list
    """
    sent_notifications.append({
        "event": event_type,
        "message": message,
        "channels": channels
    })
    return True

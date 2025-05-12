import datetime
from collections import defaultdict

def run_batch(messages):
    """
    messages: list of dict with keys 'timestamp' (ISO str), 'device_id', 'status'
    returns dict with 'hourly' and 'daily' counts per device_id
    """
    hourly = defaultdict(int)
    daily = defaultdict(int)
    now = datetime.datetime.utcnow()
    for msg in messages:
        # only count successful ('ok') messages
        if msg.get('status') != 'ok':
            continue
        ts = datetime.datetime.fromisoformat(msg['timestamp'])
        delta = now - ts
        # hourly: events in the last 1 hour (strictly less than 1h)
        if delta < datetime.timedelta(hours=1):
            hourly[msg['device_id']] += 1
        # daily: events in the last 24 hours (strictly less than 24h)
        if delta < datetime.timedelta(days=1):
            daily[msg['device_id']] += 1
    return {'hourly': dict(hourly), 'daily': dict(daily)}

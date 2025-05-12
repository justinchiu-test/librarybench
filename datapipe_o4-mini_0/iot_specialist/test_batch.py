import datetime
from telemetry.batch import run_batch

def test_run_batch():
    now = datetime.datetime.utcnow()
    msgs = [
        {'timestamp': (now - datetime.timedelta(minutes=30)).isoformat(), 'device_id': 'd1', 'status': 'ok'},
        {'timestamp': (now - datetime.timedelta(hours=2)).isoformat(), 'device_id': 'd1', 'status': 'ok'},
        {'timestamp': (now - datetime.timedelta(hours=5)).isoformat(), 'device_id': 'd2', 'status': 'fail'},
        {'timestamp': (now - datetime.timedelta(days=1)).isoformat(), 'device_id': 'd1', 'status': 'ok'},
    ]
    res = run_batch(msgs)
    assert res['hourly'] == {'d1': 1}
    # daily includes those within 24h only
    assert 'd2' not in res['daily'] or res['daily']['d2'] == 0
    assert res['daily']['d1'] == 2

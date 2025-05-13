import time
import pytest
from fs_watcher import Watcher

def test_filters_exclude():
    watcher = Watcher()
    watcher.set_filters(include=['*.py'], exclude=['test_*.py'])
    received = []
    watcher.on_event(lambda e: received.append(e))
    watcher._emit_event({'type':'mod','path':'good.py','timestamp':time.time()})
    watcher._emit_event({'type':'mod','path':'test_bad.py','timestamp':time.time()})
    time.sleep(0.1)
    assert len(received) == 1
    assert received[0]['path'] == 'good.py'

def test_throttle_limits():
    watcher = Watcher()
    watcher.set_throttle(2, 500)  # 2 events per 0.5s
    received = []
    watcher.on_event(lambda e: received.append(e))
    # send 3 events quickly
    for i in range(3):
        watcher._emit_event({'type':'e','path':f'f{i}','timestamp':time.time()})
    time.sleep(0.1)
    assert len(received) == 2
    # after window, should allow again
    time.sleep(0.6)
    watcher._emit_event({'type':'e2','path':'x','timestamp':time.time()})
    time.sleep(0.1)
    assert any(e['type']=='e2' for e in received)

import datetime
from telemetry.window import tumbling_window, sliding_window

def test_tumbling_window():
    base = datetime.datetime(2021,1,1,12,0,0)
    events = []
    for i in range(3):
        ts = (base + datetime.timedelta(seconds=i*20)).isoformat()
        events.append((ts, i))
    buckets = tumbling_window(events, window_size=60)
    # All in same window
    assert len(buckets) == 1
    vals = list(buckets.values())[0]
    assert vals == [0,1,2]

def test_sliding_window():
    vals = [1,2,3,4]
    sw = sliding_window(vals, 2)
    assert sw == [[1,2],[2,3],[3,4]]
